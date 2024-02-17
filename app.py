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

#-----------------------------------------------------Home page--------------------------------------------------------------
@app.route('/')
def home():
    return render_template('landingpage.html')

#-------------------------------------------------------signup page----------------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    session.pop('user', None)
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']  # Capture username from the form
        
        try:
            # Create user with email and password
            user = auth.create_user_with_email_and_password(email, password)
            # Set display name for the user
            auth.update_profile(user['idToken'], {'displayName': username})
            
            session['user'] = user['localId']
            return redirect(url_for('dashboard'))
        except Exception as e:
            error = "An error occurred while creating your account."
            return render_template('error.html', error=error)
    return render_template('signup.html')


#-------------------------------------------------------Sign in page-----------------------------------------------------------
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
            
            # Retrieve user data
            user_info = auth.get_account_info(user['idToken'])
            # Extract username
            username = user_info['users'][0].get('displayName', "Admin")
            print(username)
            return render_template('dashboard.html', username=username)
        except Exception as e:
            error = "Authentication failed. Please check your email and password."
            return render_template('error.html', error=error)
    return render_template('signup.html')

#----------------------------------------------forgot password-----------------------------------------------------

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

#-------------------------------------------------Dashboard page---------------------------------------------------

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user_id = session['user']
        return render_template('dashboard.html')
    else:
        # If user is not in session, redirect to sign-in page
        return redirect(url_for('signin'))

#-------------------------------------------------logout page------------------------------------------------------
@app.route('/logout')
def logout():
    # Clear the user's session
    session.pop('user', None)
    # Redirect to the signin page
    return redirect(url_for('signin'))

#-------------------------------------------------Livestock data page----------------------------------------------
# Function to check if the cow ID already exists for the user
def check_cow_id(user_id, cow_id):
    livestock_data = db.child("users").child(user_id).child("livestock").get()
    if livestock_data:
        for cow in livestock_data.each():
            if cow.val().get("cow_id") == cow_id:
                return True  # Cow ID already exists for the user
    return False  # Cow ID doesn't exist for the user

# Route for adding livestock information
@app.route('/livestock', methods=['GET', 'POST'])
def livestock():
    if 'user' not in session:
        return redirect(url_for('signin'))  # Redirect to sign-in page if user is not authenticated

    user_id = session['user']

    if request.method == 'POST':
        # Handle form submission
        cow_id = request.form['cow_id']
        breed = request.form['breed']
        dob = request.form['dob']
        avg_milk = request.form['avg_milk']
        buying_price = request.form['buying_price']

        # Check if the cow ID already exists for the user
        existing_cows = db.child("users").child(user_id).child("livestock").get().val()
        if existing_cows and any(cow['cow_id'] == cow_id for cow in existing_cows.values()):
            return render_template('error.html', error="Cow ID already exists. Please choose a different ID.")

        # Push livestock data to Firebase under the user's node
        try:
            db.child("users").child(user_id).child("livestock").push({
                "cow_id": cow_id,
                "breed": breed,
                "dob": dob,
                "avg_milk": avg_milk,
                "buying_price": buying_price
            })
        except Exception as e:
            return render_template('error.html', error=str(e))

    # Fetch the keys (child paths) under the "livestock" node
    livestock_data = db.child("users").child(user_id).child("livestock").order_by_child("cow_id").get().val()
    return render_template('livestock.html', livestock_data=livestock_data)


#------------------------------------------------Machine learning integration--------------------------------------

# Specify the upload folder inside the static directory
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Specify the allowed extensions for file uploads
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Load the pre-trained model
loaded_model = load_model(r'C:\Users\proma\Desktop\FINAL YEAR PROJECT\RESNET-50-v1(gokul).h5')

# Function to check if the file has allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function for contrast stretching
def contrast_stretching(img):
    if img.shape[-1] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    min_val, max_val, _, _ = cv2.minMaxLoc(img)
    stretched_img = np.uint8((img - min_val) / (max_val - min_val) * 255)

    if len(stretched_img.shape) == 2:
        stretched_img = cv2.cvtColor(stretched_img, cv2.COLOR_GRAY2BGR)

    return stretched_img

# Function to preprocess the image
def preprocess_image(img_path):
    img = cv2.imread(img_path)

    if img is None:
        print(f"Error: Unable to load image from {img_path}")
        return None

    img = contrast_stretching(img)

    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img, axis=0)
    img = tf.keras.applications.resnet50.preprocess_input(img)

    return img

# Function to predict the image
def predict_image(model, preprocessed_image):
    predictions = model.predict(preprocessed_image)
    return predictions

def clear_uploads_folder():
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

@app.route('/disease_prediction')
def disease_prediction():
    clear_uploads_folder()
    return render_template('disease_prediction.html') 

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return render_template('error.html',error = 'No file found')

    file = request.files['file']

    if file.filename == '':
        return render_template('error.html',error = 'No file found')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        image_url = url_for('static', filename='uploads/' + filename)
        preprocessed_image = preprocess_image(file_path)

        if preprocessed_image is not None:
            predictions = loaded_model.predict(preprocessed_image)
            predicted_class = (predictions > 0.65).astype(int).flatten()[0]

            if predicted_class == 0:
                xem = (predictions > 0.5).astype(int).flatten()[0]
                if xem == 1:
                    prediction_result = "The cow may have an infection"
                else:
                    prediction_result = "The uploaded image is predicted to be healthy."
            else:
                prediction_result = "The uploaded image is predicted to be infected."

            return render_template('prediction_result.html', prediction=prediction_result, image_url=image_url)
        else:
            return "Error in image preprocessing."
    else:
        return "File type not allowed"


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
    db = firebase.database()  # Initialize the Firebase database

    app.run(debug=True)
