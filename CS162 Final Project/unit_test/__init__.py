from web.foodapp import *
from web.firestore.main import *
from web import create_app
app = create_app()
import unittest
import os
import tempfile


class GeneralTesting(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()
    
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])