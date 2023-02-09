from web.foodapp import *
from web.firestore.main import *
from web import create_app
app = create_app()
from unit_test import GeneralTesting
from web.geoapify.main import *

class DatabaseTesting(GeneralTesting):
    def setUp(self):
        super(DatabaseTesting, self).setUp()
    
    def tearDown(self):
        super(GeneralTesting, self).setUp()
    
    def testRestaurantallergies(self):
        '''
        Testing to see if all the restaurants allergy-unfriendly options are being stored correctly
        '''
        restaurant = check_rest_allergies("Gratitude")
        self.assertEqual(restaurant, {'Gluten'})
        
    def testRestaurantdiets(self):
        '''
        Testing to see if all the restaurants diet-unfriendly options are being stored correctly
        '''
        restaurant = check_rest_diets("Gratitude")
        self.assertEqual(restaurant, {'Koscher','Pescaterian','Halal','Vegetarian'})
        get_user_location()
        
    def testRestaurantSetUp(self):
        '''
        Using the function that initializes the restaurants diet and allergy data
        '''
        #removing data first
        all_restaurants = get_all_places()
        for restaurant in all_restaurants:
            #updating them again
            update_restaurant_allergies_diets(r=restaurant)
        self.testRestaurantallergies()
        self.testRestaurantdiets()

        
    def testGeocode(self):
        """
        Test the geocode api call function
        Given a free text of address, return longitude and latitude

        Note that I use the answer on Google Maps to check if the APi works well
        I also round the number of digits to 3 to account for variations in different APIs
        """
        # recommended text to include street, number and city!
        ## TODO: in frontend of search bar, we should include recommended flash to instruct the user!
        # residence hall for M24s
        address = 'gorriti 6066, buenos aires'
        coordinates = geocode(address=address)
        assert round(coordinates[0], 3) == -34.581
        assert round(coordinates[1], 3) == -58.442
        
        # residence hall for M23s
        address = 'esmeralda 920, buenos aires'
        coordinates = geocode(address=address)
        assert round(coordinates[0], 3) == -34.597
        assert round(coordinates[1], 3) == -58.378

    def testFilterAllergy(self):
         '''
         Testing to see if foods are correctly being filtered according to an allergy
         '''
         allergy_food = filter_allergies("sorrentinos", ["Tree Nut", "Peanut"])
         self.assertTrue(allergy_food)
         allergy_food_false = filter_allergies("cheese and tomato croissant", ["Milk", "Egg", "Peanut"])
         self.assertFalse(allergy_food_false)

    def testFilterDietsFoodsF(self):
         """
         Testing if the function that filters food based on diets.
         """

         filter_diets_food_true = filter_diets("curry verde", ["Vegan"] )
         self.assertTrue(filter_diets_food_true)
         filter_diets_food_false = filter_diets("ensalada de langostinos", ["Vegan", "Vegetarian"] )
         self.assertFalse(filter_diets_food_false)