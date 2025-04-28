from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import bcrypt
import jwt
import datetime
from pymongo import MongoClient
from bson import ObjectId
app = Flask(__name__)

# MySQL bağlantı ayarları
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'birboyutasabit5546'
app.config['MYSQL_DB'] = 'ecommerce_db'

mysql = MySQL(app)

# MongoDB bağlantısını kurma
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['ecommerce_db']
cart_collection = mongo_db['carts']
product_collection = mongo_db['products']

# Kullanıcı kayıt endpoint'i
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        role = data['role']

        # Şifre hash'leme
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # MySQL veritabanına veri ekleme
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)", 
                    (email, hashed_password.decode('utf-8'), role))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Kullanıcı başarıyla kaydedildi!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Token oluşturma fonksiyonu
def generate_jwt(email, role):
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)  # Token geçerlilik süresi 
    }
    secret_key = "birboyutasabit5546"
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

# Token doğrulama fonksiyonu
def validate_jwt(token):
    try:
        secret_key = "birboyutasabit5546"
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": "Token süresi doldu"}
    except jwt.InvalidTokenError:
        return {"error": "Geçersiz Token"}

# Kullanıcı giriş endpoint'i
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        # Kullanıcının bilgilerini kontrol etme
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')): # user[3] → role  veri tabaında veriler hangi indisle saklanıyor ona dikkat et
            token = generate_jwt(email, user[3])  # Rol bilgisi token'e ekleniyor burda
            return jsonify({"token": token}), 200
        else:
            return jsonify({"error": "Geçersiz e-posta veya şifre"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Profil görüntüleme endpoint'i
@app.route('/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    try:
        token = auth_header.split(" ")[1]
        decoded_token = validate_jwt(token)

        if "error" in decoded_token:
            return jsonify(decoded_token), 401

        return jsonify({
            "message": "Profil bilgisi görüntüleniyor!",
            "email": decoded_token['email'],
            "role": decoded_token['role']  # Rol bilgisi döndürülüyor burda
        }), 200
    except IndexError:
        return jsonify({"error": "Token formatı hatalı!"}), 400

