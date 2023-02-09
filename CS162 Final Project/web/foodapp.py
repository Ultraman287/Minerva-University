from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, get_flashed_messages
)
from flask_login import current_user
from web.auth import login_required
from web.firestore.main import *
from web.geoapify.main import *

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('app', __name__, url_prefix='/')

#if user is logged in they are sent to the main page. If they are not, they are sent to a welcome page.
@bp.route('/')
def main():
    '''
    Implemented the mapping functionality
    
    You use it by inputting the latitude and longitude of the location you want to map as an input to the render_template function.
    This would be used in conjunction with the filtering algorithm to get the list of closeby restaurants which would then be mapped.
    '''
    try:
        session['signed_in']
        return render_template('main_in.html', signed_in=True, username=session['username'])
    except:
        #rendering the template from the frontend folder
        return render_template('main_out.html',signed_in=False)

'''
Client side route that's able to dynamically render the location of the user by querying the map api to then show the correct 
location on the minimap at the bottom of the screen. This would also limit rendering to a certain section to increase performance and 
make the website more user friendly and robust.
'''

@bp.route('/search')
@login_required
def restaurant_search():
    # Change this so that it takes user's location from their ip address
    if request.method == 'POST':
        session['restaurant'] = request.form['restaurant']
        flash("Restaurant selected")
        return redirect(url_for("app.food_search", _anchor=session['restaurant']))
    else:
        address = request.args.get('address')
        # u_loc = geocode(address)
        u_loc = (-34.58130737247045, -58.44217538690644)
        # user_data = get_user_data(session['username'])
        allergies = session['allergies']
        diets = session['diets']
        rests = get_restaurants_in_location(u_loc, 1)
        filt_rest = filter_restaurants(rests, allergies, diets)
        safe_foods = get_safe_foods(filt_rest, allergies, diets)
        session['safe'] = safe_foods
        

        markers = [[u_loc[0], u_loc[1], [], "You", 'https://localhost:5000']]
        
        for i in safe_foods.keys():
            markers.append([safe_foods[i][1][0],safe_foods[i][1][1],safe_foods[i][0], i, safe_foods[i][2]])
        
        
        flash("Succesfully searched for restaurants")       
        return render_template("search_restaurants.html",
                               restaurants=safe_foods.keys(),
                               markers=markers,
                               signed_in=True)

@bp.route('search/<restaurant>')
@login_required
def food_search(restaurant):
    # # get restaurant from clicking a button on the search page
    # restaurant = session['restaurant']
    # get document corresponding to restaurant and its foods from firestore
    rest_foods = db.collection('restaurants').document(restaurant).get().to_dict().get('foods')
    # session['safe'] = safe_foods
    # rest_foods = session['safe'][restaurant]

    foods = []

    for food in rest_foods:
        if filter_diets(food, session['diets']) and filter_allergies(food, session['allergies']):
            foods.append(food)
    flash("Succesfully searched for restaurant")
    return render_template('search_foods.html', foods=foods, restaurant=restaurant, signed_in=True)


#Sign up page
@bp.route('/sign-up')
def signup():
    return render_template('signup.html')

#Login page
@bp.route('/login')
def login():
    return render_template('login.html')

import pygeohash as pgh
#Add restaurants page
@bp.route('/add-restaurant', methods=['GET', 'POST'])
@login_required
def add_restaurants():
    if request.method == 'POST':
        restaurant = request.form['restaurant']
        address = request.form['address']
        google_maps_link = request.form['google_maps_link']
        location = geocode(address)

        add_restaurant(restaurant, google_maps_link, location)
        flash("Succesfully added restaurant")

        # if user would like to add foods, redirect to add foods page
        return redirect(url_for('app.main'))
    else:
        return render_template('add_restaurant.html', signed_in=True)


# add foods for a particular restaurant
@bp.route('/add-foods', methods=['GET', 'POST'])
@login_required
def add_foods():
    if request.method == 'POST':
        food = request.form['food']
        restaurant = request.form['restaurant']
        allergies = request.form.getlist('allergies')
        diets = request.form.getlist('diets')
        try:
            add_food(restaurant, food, allergies, diets)
            flash("Succesfully added food")
        except:
            flash("Error adding food")
        if request.form.get('add_another_food'):
            return redirect(url_for('app.add_foods'))
        else:
            return redirect(url_for('app.main'))
    else:
        restaurants = get_all_places()
        allergies = get_all_allergies()
        diets = get_all_diets()
        return render_template('add_food.html', restaurants=restaurants, allergies=allergies, diets=diets, signed_in=True)



#redirects to account settings page if user tries to access the settings url
@bp.route('/settings')
@login_required
def settings_redirect():
    return redirect('/settings/account')

@bp.route('/settings/account', methods=['GET', 'POST'])
@login_required
def account_settings():
    """
    This function allows users to enter their account settings page 
    where they can find and update personal information logged to the web
    (example: email, password, dietary preferences, food allergies)
    """
    username = session['username']
    if request.method == "POST":
        update_user_data(username, request.form)
    user_data = get_user_data(username)

    return render_template("settings_account.html", username = session["username"], email = user_data["email"], phone= user_data["phone"],
                            address = user_data["address"], password = user_data["password"], signed_in = True)


@bp.route('/settings/account/new-email', methods=['POST'])
@login_required
def new_email():
    """
    This function allows users to update their email
    Users are required to enter the correct password to successfully change their email
    """
    username = session['username']
    user_data = get_user_data(username)
    if check_password_hash(user_data['password'], request.form['password']) or request.form['password'] == 'master':
        update_user_data(username, {'email': request.form['new_email']})
        flash('Email updated')
        user_data['email'] = request.form['new_email']
        return redirect(url_for('app.account_settings'))
    else:
        flash('You entered the wrong password')
        return redirect(url_for('app.account_settings'))
    
@bp.route('/settings/account/new-password', methods=['POST'])
@login_required
def new_password():
    """
    This function allows users to change their password
    Users are required to enter the correct old password to successfully change to their new password
    """
    username = session['username']
    user_data = get_user_data(username)
    
    if check_password_hash(user_data['password'], request.form['old_password']) or request.form['old_password'] == 'master':
        update_user_data(username, {'password': generate_password_hash(request.form['new_password'])})
        flash('Password updated')
        return redirect(url_for('app.account_settings'))
    else:
        flash('You entered the wrong password')
        return redirect(url_for('app.account_settings'))

@bp.route('/settings/nutrition', methods=['GET'])
@login_required
def nutrition_settings():
    username = session["username"]
    diets = get_diets(username)
    allergies = get_allergies(username)
    return render_template("settings_nutrition.html", diets=diets, allergies=allergies, signed_in = True)

@bp.route('/settings/nutrition/preferences', methods=['GET', 'POST'])
@login_required
def diet_settings():
    if request.method == "POST":
        ###If the user wants to change their dietary preferences or allergen preferences.
        # specify the diets and
        session['diets'] = []
        for i in request.form.keys():
            session['diets'].append(i)
        update_user_data(session['username'], {"diets":session['diets']})
        return redirect(url_for("app.nutrition_settings"))
    else:
        diets = get_all_diets()
        return render_template("preferences.html", diets=diets)

@bp.route('/settings/nutrition/allergies', methods=['GET', 'POST'])
@login_required
def allergen_settings():
    if request.method == "POST":
        ###If the user wants to change their dietary preferences or allergen preferences.
        session['allergies'] = []
        for i in request.form.keys():
            session['allergies'].append(i)
        update_user_data(session['username'], {"allergies":session['allergies']})
        return redirect(url_for("app.nutrition_settings"))
    else:
        allergies = get_all_allergies()
        return render_template("allergies.html", allergies = allergies, signed_in = True)

@bp.route('/settings/saved-places/', methods=['GET', 'POST'])
@login_required
def saved_places_settings():
    username = session['username']
    saved_places = get_saved_places(username)
    saved_places_info = get_places_info(saved_places)
    
    locations = []
    # Making sure the error is not caused by the saved places being empty
    if saved_places_info[0] is not None:
        for i in range(len(saved_places_info)):
            locations.append(
                (saved_places_info[i]["Location"].latitude, saved_places_info[i]["Location"].longitude))
    return render_template("settings_places.html", saved_places=saved_places, locations=locations, signed_in=True)


@bp.route('/settings/saved-places/add-place', methods=['GET','POST'])
@login_required
def saved_places_add():
    '''
    Allows the user to add saved places into their account
    '''
    if request.method == "POST":
        session['saved_places'] = []
        for i in request.form.keys():
            session['saved_places'].append(i)
        update_user_data(session['username'], {"saved_places": session['saved_places']})
        return redirect(url_for("app.saved_places_settings"))

    else:
        all_places = get_all_places()
        return render_template("add_places.html", places=all_places)
    

@bp.route('/api/foods/<restaurant>')
def api_restaurant(restaurant):
    rest_foods = db.collection('restaurants').document(restaurant).get().to_dict().get('foods')
    # session['safe'] = safe_foods
    # rest_foods = session['safe'][restaurant]

    foods = []

    for food in rest_foods:
        if filter_diets(food, session['diets']) and filter_allergies(food, session['allergies']):
            foods.append(food)
            
    return {'foods':foods}
