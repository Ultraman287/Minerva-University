#from .serve import app, db

import os

from flask import Flask
from . import auth
from . import foodapp
from flask_login import LoginManager



def create_app(test_config=None):
    template_dir = os.path.abspath('frontend')
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder=template_dir, static_folder=template_dir, static_url_path='')
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )


    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    #register authentication blueprint
    app.register_blueprint(auth.bp)
    #register foodapp blueprint
    app.register_blueprint(foodapp.bp)
    
     # Using flask's inbuilt login manager to handle user sessions
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    #Using flask's inbuilt user loader to load the user from the database in a session
    
    @login_manager.user_loader
    def load_user():
        pass

    return app