from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
import pyrebase
import json

app = Flask(__name__)

# Home page
@app.route('/')
def home():
    return render_template('landingpage.html')

# Sign up page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(email, password)
            session['user'] = user['localId']
            return redirect(url_for('dashboard'))
        except Exception as e:
            return "An error occurred: " + str(e)
    return render_template('signup.html')

# Sign in page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    # Clear session when user visits sign-in page
    session.pop('user', None)
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['localId']
            return render_template('dashboard.html')
        except Exception as e:
            error = "Authentication failed. Please check your email and password."
    return render_template('signup.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
# Route for handling password reset request
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
            return "Password reset email sent. Check your inbox."
        except Exception as e:
            return "An error occurred: " + str(e)
    # Render a simple form with an input field for email
    return render_template('Passreset.html')

# Dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user_id = session['user']
        return render_template('dashboard.html')
    else:
        # If user is not in session, redirect to sign-in page
        return redirect(url_for('signup'))

if __name__ == '__main__':
    # Set the secret key for session management
    app.secret_key = '1a3f6c9e47b8d2f10e5a7b3c8f9d0e2a'
    
    # Firebase configuration
    firebaseConfig = {
        "apiKey": "AIzaSyA8Q8619M2fOJpjpqMUoqlP_l7MxBJT2y0",
        "authDomain": "s8project-e9096.firebaseapp.com",
        "databaseURL": "https://s8project-e9096-default-rtdb.asia-southeast1.firebasedatabase.app",
        "projectId": "s8project-e9096",
        "storageBucket": "s8project-e9096.appspot.com",
        "messagingSenderId": "105612683914",
        "appId": "1:105612683914:4:web:f6629fc45d8873c5a85b73"
    }

    # Initialize Firebase app
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()

    app.run(debug=True)
