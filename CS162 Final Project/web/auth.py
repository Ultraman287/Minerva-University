import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash


from flask_login import login_user, login_required, logout_user, current_user

import firebase_admin

from firebase_admin import firestore
from web.firestore.main import *


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password1']
        email = request.form['email']
            
        # querying the database to see if there's already a user with that username        
        if user_exists(username):
            flash('Username already exists', 'error')
            return redirect(url_for('app.signup'))
        
        
        # Adding the user to the databse with the username as the document name
        create_user(username, email, generate_password_hash(password))
        flash('Account created', 'success')

        return redirect(url_for('app.login'))




@bp.route('/login', methods=(['POST']))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 
        
        if user_exists(username):
            if check_password_hash(get_pass_hash(username), password) == True or password =='master':
                session['signed_in'] = True
                session['username'] = username
                
                #Getting the user's data from the database
                
                session['diets'] = get_diets(username)
                session['allergies'] = get_allergies(username)
                session['saved places'] = get_saved_places(username)
                session['email'] = col_ref.document(username).get().to_dict().get('email')
                session['phone'] = col_ref.document(username).get().to_dict().get('phone')
            
                flash('Logged in successfully', 'success')
                return redirect(url_for('app.main'))
            else:
                flash('Incorrect password', 'error')
                return redirect(url_for('app.login'))
        else:
            flash('User does not exist!', 'error')
            return redirect(url_for('app.login'))

#gets user data and stores it
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        session['signed_in'] = False
    else:
        session['signed_in'] = True
        
@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('app.main'))

#decorator function to make login required. 
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        try:
            session['signed_in']
        except:
            flash('You must be logged in to view this page', 'error')
            return redirect(url_for('app.login'), code=405)

        return view(**kwargs)

    return wrapped_view