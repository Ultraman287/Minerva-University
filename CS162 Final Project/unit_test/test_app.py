from web.foodapp import *
from web.firestore.main import *
from web import create_app
app = create_app()
from unit_test import GeneralTesting

class ApplicationTesting(GeneralTesting):
    def setUp(self):
        super(ApplicationTesting, self).setUp()
    
    def tearDown(self):
        super(GeneralTesting, self).setUp()

    def logIn(self, username, password):
        return self.app.post('/auth/login', data=dict(username=username, password=password), 
        follow_redirects = True)
    
    def logOut(self):
        return self.app.get('/auth/logout', follow_redirects=True)
    
    def testNutritionSettings(self):
        """
        Testing to see if the user can change their dietary preferences and allergen preferences.
        """
        self.logIn(username="test_user", password="test")
        # settings page
        response = self.app.get('/settings', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # test db when nothing set up yet
        diets = get_user_data("test_user")['diets']
        self.assertEqual(len(diets), 0)
        allergies = get_user_data("test_user")['allergies']
        self.assertEqual(len(allergies), 0)
        # fill preferences form
        response = self.app.get('/settings/nutrition/preferences', follow_redirects=True)
        response = self.app.post('/settings/nutrition/preferences', data=dict(Halal='', Vegan=''), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # fill allergies form
        response = self.app.get('/settings/nutrition/allergies', follow_redirects=True)
        response = self.app.post('/settings/nutrition/allergies', data=dict(Fish='', Gluten=''), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # test if user data are recorded
        diets = get_user_data("test_user")['diets']
        self.assertEqual(diets, ['Halal', 'Vegan'])
        allergies = get_user_data("test_user")['allergies']
        self.assertEqual(allergies, ['Fish', 'Gluten'])
        update_user_data("test_user", {"diets": [], "allergies": []})
        self.logOut()
    
    def testSavedPlacesSettings(self):
        '''
        testing to see if the user can change their saved places
        '''
        self.logIn(username="test_user", password="test")
        # go to page where user can add saved places
        response = self.app.get('/settings/saved-places/add-place', follow_redirects=True)
        response = self.app.post('/settings/saved-places/add-place', data=dict(Gratitude='test', Oggi='test'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # test if all places are recorded
        saved_places = get_user_data("test_user")['saved_places']
        self.assertEqual(saved_places, ['Gratitude','Oggi'])
        update_user_data("test_user", {"saved_places": []}) 
        self.logOut()