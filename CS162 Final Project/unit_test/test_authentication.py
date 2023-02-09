from web.foodapp import *
from web.firestore.main import *
from web import create_app
app = create_app()
from unit_test import GeneralTesting
from werkzeug.security import check_password_hash

class AuthenticationTesting(GeneralTesting):
    def setUp(self):
        super(AuthenticationTesting, self).setUp()
    
    def tearDown(self):
        super(GeneralTesting, self).setUp()

    def signUp(self, username, email, password):
        return self.app.post('/auth/register', 
        data=dict(username=username, email=email, password1=password, password2=password), 
        follow_redirects = True)

    def logIn(self, username, password):
        return self.app.post('/auth/login', data=dict(username=username, password=password), 
        follow_redirects = True)
    
    def logOut(self):
        return self.app.get('/auth/logout', follow_redirects=True)
    
    def updatePassword(self, old_password, new_password):
        return self.app.post('/settings/account/new-password', data=dict(old_password=old_password, new_password=new_password),
        follow_redirects=True)
    
    def updateEmail(self, new_email, password):
        return self.app.post('/settings/account/new-email', data=dict(new_email=new_email, password=password), follow_redirects=True)

    def testSignUp(self):
        """
        Sign up successfully - hashed password is saved in the database!
        """
        response = self.signUp(username="ngttam_minerva_vn", email = "ngttam@gmail.com", password="hello1234")
        assert b'Account created' in response.data
        holder = get_pass_hash("ngttam_minerva_vn")
        self.assertTrue(check_password_hash(holder, "hello1234"))
        db.collection('user').document("ngttam_minerva_vn").delete()

    def testSignUpDuplicate(self):
        """
        Sign up unsuccessfully - expected errors flashed!
        """
        self.signUp(username="ngttam_minerva_vn", email="ngttam@gmail.com", password="hello1234")
        self.assertTrue(check_password_hash(get_pass_hash("ngttam_minerva_vn"), "hello1234"))
        response = self.signUp(username="ngttam_minerva_vn", email="ngttam3010@gmail.com", password="hi1234")
        assert b'Username already exists' in response.data
        db.collection('user').document("ngttam_minerva_vn").delete()

    def testLoginLogout(self):
        """
        Test login and logout
        """
        self.signUp(username="ngttam_minerva_vn", email="ngttam@gmail.com", password="hello1234")
        self.assertTrue(check_password_hash(get_pass_hash("ngttam_minerva_vn"), "hello1234"))
        response = self.logIn(username="ngttam_minerva_vn", password="hello1234")
        assert response.status_code == 200
        assert b'Logged in successfully' in response.data
        response2 = self.logOut()
        assert response2.status_code == 200
        assert b'Logged out successfully' in response2.data
        db.collection('user').document("ngttam_minerva_vn").delete()

    def testLogInExceptions(self):
        """
        Test failures in login
        no user - wrong password - wrong username
        """
        self.signUp(username="ngttam_minerva_vn", email="ngttam@gmail.com", password="hello1234")
        self.assertTrue(check_password_hash(get_pass_hash("ngttam_minerva_vn"), "hello1234"))
        response1 = self.logIn(username="hello", password="hello1234")
        assert b'User does not exist!' in response1.data
        response2 = self.logIn(username="ngttam_minerva_vn", password="hello")
        assert b'Incorrect password' in response2.data
        db.collection('user').document("ngttam_minerva_vn").delete()
    
    def testPasswordUpdate(self):
        """
        Test password update
        Update password 
        - successful
        - wrong old password, error
        
        LOGIN
        - enter new password, successful login
        - enter old password, erorr
        """
        self.signUp(username="ngttam_minerva_vn", email="ngttam@gmail.com", password="hello1234")
        self.assertTrue(check_password_hash(get_pass_hash("ngttam_minerva_vn"), "hello1234"))
        self.logIn(username="ngttam_minerva_vn", password="hello1234")
        response1 = self.updatePassword("hi1234", "hello12345")
        assert b'You entered the wrong password' in response1.data
        response2 = self.updatePassword("hello1234", "hi1234")
        assert b'Password updated' in response2.data
        self.logOut()
        response3 = self.logIn(username="ngttam_minerva_vn", password="hello12345")
        assert b'Incorrect password' in response3.data
        response4 = self.logIn(username="ngttam_minerva_vn", password="hi1234")
        assert b'Logged in successfully' in response4.data
        db.collection('user').document("ngttam_minerva_vn").delete()
    
    def testEmailUpdate(self):
        """
        Test if email is updated successfully
        Password - another security layer
        - user needs to enter the correct password first
        - otherwise, please re-enter the password

        Update email
        - check if the new email is recorded in database
        """
        self.signUp(username="ngttam_minerva_vn", email="ngttam@gmail.com", password="hello1234")
        self.assertTrue(check_password_hash(get_pass_hash("ngttam_minerva_vn"), "hello1234"))
        self.logIn(username="ngttam_minerva_vn", password="hello1234")
        # wrong password --> fail the security check
        response = self.updateEmail(new_email="ngttam3010@uni.minerva.edu", password="hi01234")
        assert b'You entered the wrong password' in response.data
        response = self.updateEmail(new_email="ngttam3010@uni.minerva.edu", password="hello1234")
        assert b'Email updated' in response.data
        email = get_email(username="ngttam_minerva_vn")
        self.assertEqual(email, "ngttam3010@uni.minerva.edu")
        db.collection('user').document("ngttam_minerva_vn").delete()