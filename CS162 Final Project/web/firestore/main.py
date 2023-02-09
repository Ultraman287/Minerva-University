from geopy import distance
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from dotenv import load_dotenv
import google.cloud


load_dotenv()
# Connect to Firebase
from dotenv import load_dotenv

load_dotenv()


#Firebase runs independent of Flask, so if Flask restarts and the code in the if statement is run again, then Firebase will throw an error. This prevents us from initializing the firebase app twice and prevents the error.
cred =credentials.Certificate(os.environ['DB_KEY'])
firebase_admin.initialize_app(cred, { 'databaseURL': 'https://NutriSafe.firebaseio.com/'})
db = firestore.client()
col_ref = db.collection('user')

def create_user(username, email, password_hash):
    col_ref.document(username).set({
        'email': email,
        'password': password_hash,
        'address': "",
        'phone': "",
        'diets': [],
        'allergies': []
    })

def user_exists(username):
    col_ref = db.collection('user')
    doc_ref = col_ref.document(username).get()

    return doc_ref.exists

def get_pass_hash(username):
    return db.collection('user').document(username).get().to_dict().get('password')

def get_email(username):
    return db.collection('user').document(username).get().to_dict().get('email')

def get_user_data(username):
    return db.collection('user').document(username).get().to_dict()

def update_user_data(username, dictionary):
    """
    General function to update user data for a particular user
    """
    db.collection('user').document(username).update(dictionary)

def get_diets(username):
    """
    Gets the list of diets for a user.
    """
    try:
        diets = db.collection('user').document(username).get().to_dict().get('diets')
        return diets
    #Occurs because of NoneType error when trying to query an nonexistant entry.
    except AttributeError:
        return ["No Preferences Set"]


def get_all_diets():
    """
    Gets a list of all the diets in the database.
    """
    # get a list of all document names
    lst = []
    diets = db.collection(u'diets').stream()
    for diet in diets:
        lst.append(diet.id)
    return lst

def get_allergies(username):
    """
    Gets the list of allergies for a user.
    """
    try:
        allergies = db.collection('user').document(username).get().to_dict().get('allergies')
        return allergies
    #Occurs because of NoneType error when trying to query an nonexistant entry.
    except AttributeError:
        return ["No Allergies Set"]


def get_all_allergies():
    """
    Gets a list of all the allergies in the database.
    """
    lst = []
    allergies = db.collection(u'allergies').stream()
    for allergy in allergies:
        lst.append(allergy.id)
    return lst

def get_all_places():
    """
    Gets a list of all the restaurants in the database.
    """
    lst = []
    places = db.collection(u'restaurants').stream()
    for place in places:
        lst.append(place.id)
    return lst

def get_saved_places(username):
    """
    Gets the list of saved places for a user.
    """
    try:
        places = db.collection('user').document(username).get().to_dict().get('saved_places')
        if places is None:
            places = ["No Places Saved"]
        return places
    #Occurs because of NoneType error when trying to query an nonexistant entry.
    except AttributeError:
        return ["No Places Saved"]


def get_places_info(places):
    """
    Gets the document for a list of restaurants (foods, location, allergen/diet information).
    """
    places_info = []
    for place in places:
        places_info.append(db.collection('restaurants').document(place).get().to_dict())
    return places_info

def check_rest_allergies(restaurant):
    """
    Parses through all the foods in the restaurant and returns a set of all the diets represented.

    Note, the implementatino of this function is different than check_rest_diets.
    If a food is labeled with an allergy, it IS NOT safe for a user with that allergy to eat it.
    Meanwhile, if a food is labeled with a diet, it IS actually safe for a user with that diet to eat it.

    Thus, this function gets all diets stored in the database and checks if there is an overlap between the allergies
    contained in the restaurants' foods and all the allergies in general. What this means is that unless all foods
    in the restaurants contain an allergen, the restaurant is safe for that particular allergy.

    :param restaurant: The name of the restaurant
    """
    allergies = set(get_all_allergies())
    foods_lst = db.collection(u'restaurants').document(restaurant).get().to_dict().get('foods')
    for food in foods_lst:
        # get food allergies from foods collection
        food_allergies = db.collection(u'foods').document(food).get().to_dict().get('allergies')
        allergies = allergies.intersection(food_allergies)
    return allergies

def check_rest_diets(restaurant):
    """
    Parses through all the foods in the restaurant and returns a set of all the diets represented.
    :param restaurant: The name of the restaurant
    """
    diets = set()
    foods_lst = db.collection(u'restaurants').document(restaurant).get().to_dict().get('foods')
    for food in foods_lst:
        # get food allergies from foods collection
        food_diets = db.collection(u'foods').document(food).get().to_dict().get('diets')
        diets = diets.union(food_diets)
    return diets


def update_rest_data(restaurant, dictionary):
    db.collection(u'restaurants').document(restaurant).update(dictionary)


def get_user_location() -> tuple:
    """
    Some magic function to get the user's current location. Currently not used.
    """
    return (0, 0)


def update_restaurant_allergies_diets(r):
    """
    Mass update function to update a restaurant with its allergies and diets.
    """

    allergy_unsafe = list(check_rest_allergies(r))
    diet_safe = list(check_rest_diets(r))
    update_rest_data(r, {'allergy_unsafe': allergy_unsafe, 'diet_safe': diet_safe})


def get_distance(loc1, loc2):
    # get distance between two locations
    dis = distance.distance(loc1, loc2).km
    return dis

import pygeohash as pgh

# add a hash to all restaurants
def add_hash():
    restaurants = get_all_places()
    for r in restaurants:
        lat = db.collection('restaurants').document(r).get().to_dict().get('Location').latitude
        long = db.collection('restaurants').document(r).get().to_dict().get('Location').longitude
        hash = pgh.encode(lat, long)
        update_rest_data(r, {'hash': hash})


def get_restaurants_in_location(location, distance):
    """
    Function to use Firestore's capacties to query for restaurants within a certain distance.

    params: location: tuple of (lat, long)
    params: distance: distance in km
    returns: a list of firestore objects corresponding to restaurants within a certain distance of a location
    """
    # convert distance from km to coordinates
    distance = (distance / 111.12)

    lowest_lat = location[0] - distance
    highest_lat = location[0] + distance
    lowest_lon = location[1] - distance
    highest_lon = location[1] + distance

    lesser_hash = pgh.encode(lowest_lat, lowest_lon)
    greater_hash = pgh.encode(highest_lat, highest_lon)

    rests = db.collection(u'restaurants').where(u'hash', u'>=', lesser_hash).where(u'hash', u'<=', greater_hash).stream()
    # get all ids of restaurants
    drests = {}
    for r in rests:
        drests[r.id] = r
    return drests


def filter_restaurants(restaurants, allergies, diets):
    """
    Filters restaurants based on whether they contain at least one item that the user might be able to consume.
    This is meant to reduce the time spent loading the page and parsing through every individual food item every
    search run, especially if the user cannot eat at the restaurant anyway.

    :param restaurants: A dictionary of restaurants to filter
    :param allergies: A list of allergies to filter by
    :param diets: A list of diets to filter by
    :return: A dictionary of restaurants that the user can eat at
    """
    if allergies == [] and diets == []:
        return restaurants
    filtered_restaurants = {}
    for r in restaurants:
        # check if restaurant is safe for allergies
        # get allergy field from document r
        allergy_unsafe = r.to_dict().get('allergy_unsafe')
        diet_safe = r.to_dict().get('diet_safe')
        if set(allergies).intersection(set(allergy_unsafe)) == set():
            # check if restaurant is safe for diets
            if set(diets).intersection(set(diet_safe)) != set():
                filtered_restaurants[r.id] = r
    print(filtered_restaurants)
    return filtered_restaurants



def filter_allergies(food, allergies):
    """
    Filters a particular food based on a preset list of allergies.
    :param food: food name
    :param allergies: list of allergies
    :return: True if food is safe for allergies, False otherwise
    """
    food_allergies = db.collection(u'foods').document(food).get().to_dict().get('allergies')

    if set(allergies).intersection(set(food_allergies)) == set():
        return True
    return False




def filter_diets(food, diets):
    """
    Filters a particular food based on a preset list of diets.
    :param food: food name
    :param diets: list of diets
    :return: True if food is okay for diets (also called preferences), False otherwise
    """
    food_diets = db.collection(u'foods').document(food).get().to_dict().get('diets')
    # return a document of the food if its diet array contains any of the diets

    # check if food is safe for diets
    if set(diets).issubset(food_diets):
        return True
    return False

def get_safe_foods(filtered_restaurants, allergies, diets):
    """
    Get safe foods from filtered restaurants

    :param filtered_restaurants: dictionary of restaurants
    :param allergies: list of allergies
    :param diets: list of diets
    """

    safe = {}
    for rest in filtered_restaurants.keys():
        rest_foods = filtered_restaurants[rest].to_dict().get('foods')
        safe_foods = []
        for food in rest_foods:
            if filter_diets(food, diets) and filter_allergies(food, allergies):
                safe_foods.append(food)
        if safe_foods == []:
            continue
        safe[rest] = (safe_foods, (filtered_restaurants[rest].to_dict().get('Location').latitude, filtered_restaurants[rest].to_dict().get('Location').longitude), filtered_restaurants[rest].to_dict().get('Google Maps Link'))

    return safe




def search(allergies, diets, u_loc=(-34.581350, -58.428000)):
    """
    Combines the workflow of several functions in the main.py page.
    Outputs a dictionary of restaurants and corresponding foods there that are safe for the user.
    Also outputs the map coordinates of the restaurant.

    :param allergies: list of allergies
    :param diets: list of diets
    :param u_loc: user location in latitude and longitude. Default: Gorriti residence.

    :return: dictionary of restaurants mapping to foods and location
    """

    rests = get_restaurants_in_location(u_loc, 5)
    filt_rest = filter_restaurants(rests, allergies, diets)
    safe_foods = get_safe_foods(filt_rest, allergies, diets)
    return safe_foods


def add_restaurant(restaurant, google_maps_link, location):
    """
    Adds a restaurant to the database
    :param restaurant: name of restaurant
    :param google_maps_link: link to google maps
    :param location: tuple of (lat, long)
    :param geohash: geohash of location
    """
    # check if matching document already exists
    geohash = pgh.encode(location[0], location[1])

    if db.collection(u'restaurants').document(restaurant).get().exists:
        return

    db.collection(u'restaurants').document(restaurant).set({
        u'Google Maps Link': google_maps_link,
        u'Location': google.cloud.firestore.GeoPoint(location[0],location[1]),
        u'hash': geohash,
        u'foods': []
    })


def add_food(restaurant, food, allergies, diets):
    """
    Adds a food to the database
    :param restaurant: name of restaurant
    :param food: name of food
    :param allergies: list of allergies
    :param diets: list of diets
    """
    # check if the restaurant already contains that food in the menu

    if food in db.collection(u'restaurants').document(restaurant).get().to_dict().get('foods'):
        return

    # add food to foods collection
    if not db.collection(u'foods').document(food).get().exists:
        db.collection(u'foods').document(food).set({
            u'allergies': allergies,
            u'diets': diets
        })

    # add food to restaurant
    db.collection(u'restaurants').document(restaurant).update({
        u'foods': firestore.ArrayUnion([food])
    })

    # update the restaurant's allergy_unsafe and diet_safe fields
    update_restaurant_allergies_diets(restaurant)