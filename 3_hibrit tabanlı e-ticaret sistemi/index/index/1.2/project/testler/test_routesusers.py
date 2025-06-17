# testler/test_routesusers.py

# --- mysql.connection override (bypass flask_mysqldb property) ---
# --- mysql.connection override (bypass flask_mysqldb property) ---
from flask_mysqldb import MySQL
from unittest.mock import MagicMock as _MagicMock
_dummy_conn = _MagicMock()
MySQL.connection = property(lambda self: _dummy_conn)
# ------------------------------------------------------------------

# -------------------------------------------------------------------

import pytest
import bcrypt
from unittest.mock import patch, MagicMock
from flask import Flask
from back.routes.routesusers import users_bp

@pytest.fixture(scope="module")
def client():
    app = Flask(__name__)
    app.register_blueprint(users_bp)
    app.config.update({
        'TESTING': True,
        'MYSQL_HOST': 'localhost',
        'MYSQL_USER': 'root',
        'MYSQL_PASSWORD': 'password',
        'MYSQL_DB': 'testdb',
        'MYSQL_PORT': 3306,
        # 'MYSQL_UNIX_SOCKET' artık gerek kalmadı, connection override ile bypass edildi
    })
    with app.test_client() as tc:
        with app.app_context():
            yield tc

# ---------- register endpoint ----------

@patch("back.routes.routesusers.mysql.connection.cursor")
def test_register_success(mock_cursor, client):
    """✅ register: yeni e-posta ile başarılı kayıt → 201"""
    cur = MagicMock()
    cur.fetchone.return_value = None
    mock_cursor.return_value = cur

    rv = client.post("/register", json={
        "email": "new@example.com",
        "password": "pw123",
        "role": "user"
    })
    assert rv.status_code == 201
    assert "başarıyla kaydedildi" in rv.get_json()["message"].lower()

@patch("back.routes.routesusers.mysql.connection.cursor")
def test_register_existing_email(mock_cursor, client):
    """❌ register: e-posta zaten kayıtlı → 400"""
    cur = MagicMock()
    cur.fetchone.return_value = ('id','a@b.com','hash','user')
    mock_cursor.return_value = cur

    rv = client.post("/register", json={
        "email":"a@b.com","password":"pw","role":"user"
    })
    assert rv.status_code == 400
    assert "zaten kayıtlı" in rv.get_json()["error"].lower()

@patch("back.routes.routesusers.mysql.connection.cursor")

def test_register_missing_fields(mock_cursor, client):

    """❌ register: eksik alan → 400 Bad Request ve doğru hata mesajı"""

    rv = client.post("/register", json={})

    assert rv.status_code == 400

    assert "e-posta alanı zorunludur" in rv.get_json()["error"].lower()

@patch("back.routes.routesusers.mysql.connection.cursor")
def test_register_db_error(mock_cursor, client):
    """❌ register: DB bağlantı/execute hatası → 500"""
    mock_cursor.side_effect = Exception("DB conn fail")
    rv = client.post("/register", json={
        "email":"x@x.com","password":"pw","role":"user"
    })
    assert rv.status_code == 500
    assert "db conn fail" in rv.get_json()["error"].lower()


def test_register_empty_email(client):
    """❌ register: email boş → 400"""
    rv = client.post("/register", json={"email":"", "password":"pw", "role":"user"})
    assert rv.status_code == 400
    assert "e-posta" in rv.get_json()["error"].lower()

def test_register_empty_password(client):
    """❌ register: parola boş → 400"""
    rv = client.post("/register", json={"email":"a@b.com", "password":"", "role":"user"})
    assert rv.status_code == 400
    assert "parola" in rv.get_json()["error"].lower()

def test_register_empty_role(client):
    """❌ register: role boş → 400"""
    rv = client.post("/register", json={"email":"a@b.com", "password":"pw", "role":""})
    assert rv.status_code == 400
    assert "rol" in rv.get_json()["error"].lower()

# ---------- login endpoint ----------

@patch("back.routes.routesusers.generate_jwt")
@patch("back.routes.routesusers.mysql.connection.cursor")
def test_login_success(mock_cursor, mock_jwt, client):
    """✅ login: doğru mail+şifre → 200 & token"""
    fake_token = "jwt123"
    mock_jwt.return_value = fake_token
    hashed = bcrypt.hashpw(b"secret", bcrypt.gensalt()).decode('utf-8')
    cur = MagicMock()
    cur.fetchone.return_value = (1,"u@e.com",hashed,"user")
    mock_cursor.return_value = cur

    rv = client.post("/login", json={"email":"u@e.com","password":"secret"})
    assert rv.status_code == 200
    assert rv.get_json()["token"] == fake_token

@patch("back.routes.routesusers.mysql.connection.cursor")
def test_login_no_user(mock_cursor, client):
    """❌ login: kullanıcı yok → 401"""
    cur = MagicMock()
    cur.fetchone.return_value = None
    mock_cursor.return_value = cur

    rv = client.post("/login", json={"email":"nouser","password":"pw"})
    assert rv.status_code == 401
    assert "geçersiz e-posta veya şifre" in rv.get_json()["error"].lower()

@patch("back.routes.routesusers.mysql.connection.cursor")
def test_login_wrong_password(mock_cursor, client):
    """❌ login: yanlış şifre → 401"""
    hashed = bcrypt.hashpw(b"right", bcrypt.gensalt()).decode('utf-8')
    cur = MagicMock()
    cur.fetchone.return_value = (1,"u@e.com",hashed,"user")
    mock_cursor.return_value = cur

    rv = client.post("/login", json={"email":"u@e.com","password":"wrong"})
    assert rv.status_code == 401

@patch("back.routes.routesusers.mysql.connection.cursor")
def test_login_missing_fields(mock_cursor, client):
    """❌ login: eksik alan → 400"""
    rv = client.post("/login", json={"email":"u@e.com"})
    assert rv.status_code == 400
    assert "parola alanı zorunludur" in rv.get_json()["error"].lower()

def test_login_missing_email(client):
    """❌ login: email boş → 400"""
    resp = client.post("/login", json={"password":"pw"})
    assert resp.status_code == 400
    assert "e-posta alanı zorunludur" in resp.get_json()["error"].lower()

def test_login_missing_password(client):
    """❌ login: password boş → 400"""
    resp = client.post("/login", json={"email":"u@e.com"})
    assert resp.status_code == 400
    assert "parola alanı zorunludur" in resp.get_json()["error"].lower()




@patch("back.routes.routesusers.mysql.connection.cursor")
def test_login_db_error(mock_cursor, client):
    """❌ login: DB hata → 500"""
    mock_cursor.side_effect = Exception("SQL fail")
    rv = client.post("/login", json={"email":"u@e.com","password":"pw"})
    assert rv.status_code == 500
    assert "sql fail" in rv.get_json()["error"].lower()

# ---------- profile endpoint ----------

def test_profile_no_token(client):
    """❌ profile: Authorization header yok → 401"""
    rv = client.get("/profile")
    assert rv.status_code == 401
    assert "token bulunamadı" in rv.get_json()["error"].lower()

@patch("back.routes.routesusers.validate_jwt")
def test_profile_bad_format(mock_val, client):
    """❌ profile: header format hatalı → 400"""
    rv = client.get("/profile", headers={"Authorization":"Bad"})
    assert rv.status_code == 400
    assert "formatı hatalı" in rv.get_json()["error"].lower()

@patch("back.routes.routesusers.validate_jwt")
def test_profile_empty_token(mock_val, client):
    """❌ profile: Bearer sonrası token boş → 401"""
    mock_val.return_value = {"error":"Geçersiz Token"}
    rv = client.get("/profile", headers={"Authorization":"Bearer "})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Geçersiz Token"

@patch("back.routes.routesusers.validate_jwt")
def test_profile_invalid_token(mock_val, client):
    """❌ profile: geçersiz token → 401"""
    mock_val.return_value = {"error":"Geçersiz Token"}
    rv = client.get("/profile", headers={"Authorization":"Bearer bad"})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Geçersiz Token"

@patch("back.routes.routesusers.validate_jwt")
def test_profile_expired_token(mock_val, client):
    """❌ profile: token süresi doldu → 401"""
    mock_val.return_value = {"error":"Token süresi doldu"}
    rv = client.get("/profile", headers={"Authorization":"Bearer expired"})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token süresi doldu"

@patch("back.routes.routesusers.validate_jwt")
def test_profile_success(mock_val, client):
    """✅ profile: geçerli token → 200 & email/role döner"""
    mock_val.return_value = {"email":"u@e.com","role":"user"}
    rv = client.get("/profile", headers={"Authorization":"Bearer tok"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["email"] == "u@e.com"
    assert data["role"] == "user"

# ---------- forgot-password endpoint ----------

@patch("back.routes.routesusers.send_email")
@patch("back.routes.routesusers.generate_jwt")
@patch("back.routes.routesusers.mysql.connection.cursor")
def test_forgot_password_success(mock_cursor, mock_jwt, mock_send, client):
    """✅ forgot-password: kullanıcı varsa e-posta gönder → 200"""
    mock_jwt.return_value = "resettoken"
    cur = MagicMock()
    cur.fetchone.return_value = (1,"u@e.com","h","r")
    mock_cursor.return_value = cur

    rv = client.post("/forgot-password", json={"email":"u@e.com"})
    assert rv.status_code == 200
    mock_send.assert_called_once_with("u@e.com","resettoken")

@patch("back.routes.routesusers.mysql.connection.cursor")
def test_forgot_password_not_found(mock_cursor, client):
    """❌ forgot-password: kullanıcı yok → 404"""
    cur = MagicMock()
    cur.fetchone.return_value = None
    mock_cursor.return_value = cur

    rv = client.post("/forgot-password", json={"email":"x@x.com"})
    assert rv.status_code == 404

@patch("back.routes.routesusers.mysql.connection.cursor")
def test_forgot_password_missing_field(mock_cursor, client):
    """❌ forgot-password: email eksik → 400"""
    rv = client.post("/forgot-password", json={})
    assert rv.status_code == 400
    assert "e-posta alanı zorunludur" in rv.get_json()["error"].lower()

@patch("back.routes.routesusers.mysql.connection.cursor")
def test_forgot_password_db_error(mock_cursor, client):
    """❌ forgot-password: DB hata → 500"""
    mock_cursor.side_effect = Exception("Forgot DB err")
    rv = client.post("/forgot-password", json={"email":"u@e.com"})
    assert rv.status_code == 500
    assert "forgot db err" in rv.get_json()["error"].lower()

# ---------- reset-password endpoint ----------

@patch("back.routes.routesusers.validate_jwt")
@patch("back.routes.routesusers.mysql.connection.cursor")
def test_reset_password_success(mock_cursor, mock_val, client):
    """✅ reset-password: geçerli token+şifre → 200"""
    mock_val.return_value = {"email":"u@e.com"}
    rv = client.post("/reset-password", json={
        "token":"good","new_password":"newpw"
    })
    assert rv.status_code == 200

@patch("back.routes.routesusers.validate_jwt")
def test_reset_password_invalid_token(mock_val, client):
    """❌ reset-password: geçersiz token → 401"""
    mock_val.return_value = {"error":"Geçersiz Token"}
    rv = client.post("/reset-password", json={
        "token":"bad","new_password":"pw"
    })
    assert rv.status_code == 401

@patch("back.routes.routesusers.validate_jwt")
def test_reset_password_expired_token(mock_val, client):
    """❌ reset-password: süresi dolmuş token → 401"""
    mock_val.return_value = {"error":"Token süresi doldu"}
    rv = client.post("/reset-password", json={
        "token":"expired","new_password":"pw"
    })
    assert rv.status_code == 401

def test_reset_password_missing_token(client):
    """❌ reset-password: token eksik → 400"""
    rv = client.post("/reset-password", json={"new_password":"pw"})
    assert rv.status_code == 400
    assert "token zorunludur" in rv.get_json()["error"].lower()

def test_reset_password_empty_token(client):
    """❌ reset-password: token boş → 400"""
    rv = client.post("/reset-password", json={
        "token":"", "new_password":"pw"
    })
    assert rv.status_code == 400

def test_reset_password_missing_new_password(client):
    """❌ reset-password: new_password eksik → 400"""
    rv = client.post("/reset-password", json={"token":"t"})
    assert rv.status_code == 400

def test_reset_password_empty_new_password(client):
    """❌ reset-password: new_password boş → 400"""
    rv = client.post("/reset-password", json={
        "token":"t","new_password":""
    })
    assert rv.status_code == 400

@patch("back.routes.routesusers.validate_jwt")
@patch("back.routes.routesusers.mysql.connection.cursor")
def test_reset_password_db_error(mock_cursor, mock_val, client):
    """❌ reset-password: DB güncelleme hatası → 500"""
    mock_val.return_value = {"email":"u@e.com"}
    cur = MagicMock()
    cur.execute.side_effect = Exception("Reset DB fail")
    mock_cursor.return_value = cur

    rv = client.post("/reset-password", json={
        "token":"t","new_password":"pw"
    })
    assert rv.status_code == 500
    assert "reset db fail" in rv.get_json()["error"].lower()



# cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
#   pytest testler/test_routesusers.py