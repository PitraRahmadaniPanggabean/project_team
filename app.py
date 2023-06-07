from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

SECRET_KEY = "SPARTA"

MONGODB_CONNECTION_STRING = "mongodb+srv://2002:2002@cluster0.gx21kg4.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbupdate




if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)