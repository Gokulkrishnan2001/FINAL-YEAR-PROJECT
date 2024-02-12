from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

app = Flask(__name__)

