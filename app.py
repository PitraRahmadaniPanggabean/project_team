from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

SECRET_KEY = 'SPARTA'

MONGODB_CONNECTION_STRING = 'mongodb+srv://2002:2002@cluster0.gx21kg4.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbbig

TOKEN_KEY = 'mytoken'

@app.route("/")
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.dataregist.find_one({"username": payload["id"]})
        return render_template("index.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was a problem logging you in"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ktp = request.form.get('KTP')
        password = hashlib.sha256(request.form.get('password', '').encode()).hexdigest()

        if ktp and password:
            user_info = db.dataregist.find_one({"ktp": ktp, "password": password})
            if user_info:
                token = jwt.encode({"id": ktp, "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")
                response = make_response(redirect(url_for('home')))
                response.set_cookie("mytoken", token, httponly=True)
                return response

        return render_template('login.html', error_message='Invalid login credentials')
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['nama']
        email = request.form['email']
        password = hashlib.sha256(request.form['inputPassword'].encode()).hexdigest()
        ktp = request.form['KTP']
        telp = request.form['inputnoTelp']
        address = request.form['inputAddress']

        db.dataregist.insert_one({
            'name': name,
            'email': email,
            'password': password,
            'ktp': ktp,
            'telp': telp,
            'address': address
        })

        return redirect(url_for('home'))
    else:
        return render_template('register.html')
    


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
