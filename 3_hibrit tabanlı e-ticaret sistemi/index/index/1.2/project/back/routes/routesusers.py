from flask import Blueprint, request, jsonify
import bcrypt
from back.database import mysql
from back.auth import generate_jwt, validate_jwt
from back.util.email_utils import send_email

users_bp = Blueprint("users", __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        # Zorunlu alan kontrolleri
        if not data.get('email'):
            return jsonify({"error": "E-posta alanı zorunludur!"}), 400
        if not data.get('password'):
            return jsonify({"error": "Parola alanı zorunludur!"}), 400
        if not data.get('role'):
            return jsonify({"error": "Rol alanı zorunludur!"}), 400

        email = data['email']
        password = data['password']
        role = data['role']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            cur.close()
            return jsonify({"error": "Bu e-posta adresi zaten kayıtlı."}), 400

        cur.execute(
            "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
            (email, hashed_password.decode('utf-8'), role)
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Kullanıcı başarıyla kaydedildi!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/login', methods=['POST'])
def login():
    # JSON alan kontrolü
    data = request.get_json() or {}
    if not data.get('email'):
        return jsonify({"error": "E-posta alanı zorunludur!"}), 400
    if not data.get('password'):
        return jsonify({"error": "Parola alanı zorunludur!"}), 400

    try:
        email = data['email']
        password = data['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            token = generate_jwt(email, user[3])
            return jsonify({"token": token}), 200
        return jsonify({"error": "Geçersiz e-posta veya şifre"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401
    try:
        token = auth_header.split(" ")[1]
        decoded = validate_jwt(token)
        if "error" in decoded:
            return jsonify(decoded), 401
        return jsonify({
            "message": "Profil bilgisi görüntüleniyor!",
            "email": decoded['email'],
            "role": decoded['role']
        }), 200
    except IndexError:
        return jsonify({"error": "Token formatı hatalı!"}), 400

@users_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json() or {}
        if not data.get('email'):
            return jsonify({"error": "E-posta alanı zorunludur!"}), 400
        email = data['email']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        if not user:
            return jsonify({"error": "Kullanıcı bulunamadı!"}), 404
        reset_token = generate_jwt(email, "password_reset")
        send_email(email, reset_token)
        return jsonify({"message": "Şifre sıfırlama bağlantısı e-posta ile gönderildi!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json() or {}
        token = data.get('token')
        new_password = data.get('new_password')
        if not token:
            return jsonify({"error": "Token zorunludur!"}), 400
        if not new_password:
            return jsonify({"error": "Yeni şifre zorunludur!"}), 400
        decoded = validate_jwt(token)
        if "error" in decoded:
            return jsonify(decoded), 401
        email = decoded['email']
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (hashed.decode('utf-8'), email)
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Şifre başarıyla güncellendi!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500