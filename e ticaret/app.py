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

# Ürün ekleme endpoint'i (Sadece Tedarikçi rolü için)
@app.route('/add-product', methods=['POST'])
def add_product():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    try:
        token = auth_header.split(" ")[1]
        decoded_token = validate_jwt(token)

        if "error" in decoded_token:
            return jsonify(decoded_token), 401

        # Rol kontrolü
        if decoded_token['role'] != 'supplier':
            return jsonify({"error": "Bu işlem yalnızca Tedarikçiler için geçerlidir!"}), 403

        data = request.get_json()
        product_name = data['product_name']
        price = data['price']

        # MongoDB'ye ürün ekle
        product_collection.insert_one({
            "product_name": product_name,
            "price": price,
            "added_by": decoded_token['email']
        })

        return jsonify({"message": "Ürün başarıyla eklendi!"}), 201

    except IndexError:
        return jsonify({"error": "Token formatı hatalı!"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#Kullanıcıya Bildirim Gönderme
def send_email_to_users(user_email, product_name):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "h88542708@gmail.com"
        sender_password = "iopkjzuqwmixaxub"# uygulama şifresi kulanarak şifreyi yazdım

        subject = "Sepetinizdeki Ürün Güncellendi"
        body = f"Merhaba,\n\n'{product_name}' adlı ürün artık stokta bulunmamaktadır ve sepetinizden kaldırılmıştır. Yeni ürünlerimize göz atmayı unutmayın!"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = user_email

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()

        print("Kullanıcıya bilgilendirme e-postası gönderildi!")

    except Exception as e:
        print(f"E-posta gönderim hatası: {e}")    

# Sepete ürün ekleme endpoint'i
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    try:
        token = auth_header.split(" ")[1]
        decoded_token = validate_jwt(token)

        if "error" in decoded_token:
            return jsonify(decoded_token), 401

        user_id = decoded_token['email']

        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not product_id:
            return jsonify({"error": "Ürün ID'si zorunludur!"}), 400

        cart_collection.insert_one({
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity
        })

        # E-posta bildirimini burada ekledik
        send_email_to_users(user_id, "Sepetiniz Güncellendi!")

        return jsonify({"message": "Ürün sepete eklendi ve e-posta bildirimi gönderildi!"}), 201

    except IndexError:
        return jsonify({"error": "Token formatı hatalı!"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#a "Siparişiniz Alındı " e-postası göndermek için yeni bir endpoint oluşturuyoruz.
@app.route('/complete-cart', methods=['POST'])
def complete_cart():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    try:
        token = auth_header.split(" ")[1]
        decoded_token = validate_jwt(token)

        if "error" in decoded_token:
            return jsonify(decoded_token), 401

        user_id = decoded_token['email']

        # Sepet tamamlanır (Tüm ürünler "Tamamlandı" olarak işaretlenir)
        cart_collection.update_many(
            {"user_id": user_id},
            {"$set": {"status": "Tamamlandı"}}
        )

        # E-posta Bildirim Fonksiyonu Çağrılıyor
        send_email_to_users(user_id, "Siparişiniz Alındı!")

        return jsonify({"message": "Sepet başarıyla tamamlandı ve e-posta bildirimi gönderildi!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# Sepeti görüntüleme endpoint'i
@app.route('/get-cart', methods=['GET'])
def get_cart():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    try:
        token = auth_header.split(" ")[1]
        decoded_token = validate_jwt(token)

        if "error" in decoded_token:
            return jsonify(decoded_token), 401

        user_id = decoded_token['email']
        cart_items = list(cart_collection.find({"user_id": user_id}))

        for item in cart_items:
            item['_id'] = str(item['_id'])

        return jsonify({"cart": cart_items}), 200

    except IndexError:
        return jsonify({"error": "Token formatı hatalı!"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Ürün Güncelleme Endpoint'i
@app.route('/update-product/<product_id>', methods=['PUT'])
def update_product(product_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    try:
        token = auth_header.split(" ")[1]
        decoded_token = validate_jwt(token)

        if "error" in decoded_token:
            return jsonify(decoded_token), 401

        # Rol kontrolü
        if decoded_token['role'] != 'supplier':
            return jsonify({"error": "Bu işlem yalnızca Tedarikçiler için geçerlidir!"}), 403

        # Güncelleme için gerekli veriler
        data = request.get_json()
        product_name = data.get('product_name')
        price = data.get('price')

        if not product_name or not price:
            return jsonify({"error": "Ürün adı ve fiyat zorunludur!"}), 400

        # MongoDB'de ürünü güncelle
        result = product_collection.update_one(
            {"_id": product_id},
            {"$set": {"product_name": product_name, "price": price}}
        )

        if result.modified_count == 0:
            return jsonify({"error": "Ürün bulunamadı veya güncellenemedi!"}), 404

        return jsonify({"message": "Ürün başarıyla güncellendi!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

