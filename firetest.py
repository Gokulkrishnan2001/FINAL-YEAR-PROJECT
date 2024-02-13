import pyrebase
from flask import Flask, render_template, request, redirect, session, url_for
import json

app = Flask(__name__)

firebaseConfig = {
        "apiKey": "AIzaSyA8Q8619M2fOJpjpqMUoqlP_l7MxBJT2y0",
        "authDomain": "s8project-e9096.firebaseapp.com",
        "databaseURL": "https://s8project-e9096-default-rtdb.asia-southeast1.firebasedatabase.app",
        "projectId": "s8project-e9096",
        "storageBucket": "s8project-e9096.appspot.com",
        "messagingSenderId": "105612683914",
        "appId": "1:105612683914:4:web:f6629fc45d8873c5a85b73"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

if __name__ == '__main__':
        app.run(debug=True)