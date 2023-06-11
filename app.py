from flask import Flask, render_template, request, redirect, url_for, make_response
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

SECRET_KEY = 'SPARTA'

MONGODB_CONNECTION_STRING = 'mongodb+srv://2002:2002@cluster0.gx21kg4.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbbig

TOKEN_KEY = 'mytoken'

# Decorator untuk memvalidasi token akses
def login_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            token = request.cookies.get("token")
            if not token:
                return redirect(url_for("login"))  # Redirect ke halaman login jika token tidak ada

            user_id, user_role = validate_token(token)
            if not user_id or user_role != role:
                return redirect(url_for("login"))  # Redirect ke halaman login jika token tidak valid atau peran tidak sesuai

            # Token valid, izinkan akses ke halaman yang dituju
            return func(user_id, *args, **kwargs)

        return decorated_view

    return decorator

# Fungsi untuk memvalidasi token akses
def validate_token(token):
    try:
        # Mendekode token dan memverifikasi dengan menggunakan SECRET_KEY yang sama dengan yang digunakan pada proses login
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["id"], payload["role"]  # Mengembalikan ID dan peran (role) dari token
    except jwt.ExpiredSignatureError:
        return None, None  # Token sudah kadaluarsa
    except jwt.exceptions.DecodeError:
        return None, None  # Error dalam dekode token

@app.route("/")
@login_required("warga")
def home(user_id):
    warga_info = db.dataregist.find_one({"ktp": user_id})
    return render_template("warga_dashboard.html", warga_info=warga_info)

@app.route('/admin')
@login_required("admin")
def admin_dashboard(user_id):
    # Logic untuk halaman dashboard admin
    return render_template('admin_dashboard.html', admin_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ktp = request.form.get('KTP')
        password = hashlib.sha256(request.form.get('password', '').encode()).hexdigest()

        if ktp and password:
            user_info = db.dataregist.find_one({"ktp": ktp, "password": password})
            if user_info:
                role = user_info.get("role")  # Mendapatkan peran (role) pengguna dari MongoDB
                token = jwt.encode({"id": ktp, "role": role, "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")
                response = make_response(redirect(url_for('login'))) if role == "warga" else make_response(redirect(url_for('admin_dashboard')))
                response.set_cookie("token", token, httponly=True)
                return response

        return render_template('login.html', error_message='Invalid login credentials')
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ktp = request.form.get('KTP')
        nama = request.form.get('nama')
        password = hashlib.sha256(request.form.get('inputPassword', '').encode()).hexdigest()
        no_telp = request.form.get('inputnoTelp')
        email = request.form.get('inputemail')
        alamat = request.form.get('inputAddress')

        if ktp and nama and password and no_telp and email and alamat:
            user_info = db.dataregist.find_one({"ktp": ktp})
            if user_info:
                return render_template('register.html', error_message='User with this KTP already exists')

            db.dataregist.insert_one({"ktp": ktp, "nama": nama, "password": password, "no_telp": no_telp, "email": email, "alamat": alamat, "role": "warga"})
            return redirect(url_for('login'))  # Arahkan pengguna ke halaman login setelah registrasi berhasil

        return render_template('register.html', error_message='Please fill all the required fields')
    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('token')
    return response


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
