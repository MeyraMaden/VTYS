# testler/test_routescart.py

import sys
import os
import pytest
from bson import ObjectId
from flask import Flask
from unittest.mock import patch, MagicMock

# Proje kök dizinini path’e ekliyoruz ki back paketi import edilebilsin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from back.routes.routescart import cart_bp

@pytest.fixture
def app():
    """Flask uygulama örneği oluşturur ve cart blueprint’ini kaydeder."""
    app = Flask(__name__)
    app.register_blueprint(cart_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Flask test client’ını döner."""
    return app.test_client()

# ---------- add-to-cart endpoint tests ----------

@patch("back.routes.routescart.send_email_to_users")
@patch("back.routes.routescart.cart_collection.insert_one")
@patch("back.routes.routescart.product_collection.find_one")
@patch("back.routes.routescart.validate_jwt")
def test_add_to_cart_success(
    mock_validate, mock_find, mock_insert, mock_send, client
):
    """
    ✅ Başarılı sepete ekleme:
      - Valid token, valid product_id
      - quantity default 1 olarak eklenir
      - insert_one ve send_email_to_users çağrılır
    """
    # JWT doğrulaması başarılı, email alanı var
    mock_validate.return_value = {"email": "u@e.com"}
    # Geçerli ObjectId ve ürün bulunur
    pid = str(ObjectId())
    mock_find.return_value = {
        "_id": ObjectId(pid),
        "product_name": "P",
        "price": 10
    }

    # İstek quantity belirtmeden gönderiliyor
    rv = client.post(
        "/add-to-cart",
        json={"product_id": pid},
        headers={"Authorization": "Bearer tok"}
    )

    # Yanıt status 201 ve mesajda sepete eklendi yazmalı
    assert rv.status_code == 201
    assert "sepete eklendi" in rv.get_json()["message"].lower()

    # insert_one’ın çağrıldığı argüman kontrolü
    doc = mock_insert.call_args[0][0]
    assert doc["user_id"] == "u@e.com"
    assert doc["quantity"] == 1

    # E-posta bildirim fonksiyonu çağrıldı mı?
    mock_send.assert_called_once_with("u@e.com", "Sepetiniz Güncellendi!")

def test_add_to_cart_no_token(client):
    """
    ❌ Sepete ekleme: Authorization header olmadan 401 dönmeli
    """
    rv = client.post("/add-to-cart", json={"product_id": "x"})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token bulunamadı!"

@patch("back.routes.routescart.validate_jwt")
def test_add_to_cart_invalid_token(mock_validate, client):
    """
    ❌ Sepete ekleme: validate_jwt ‘error’ dönerse 401 dönmeli
    """
    mock_validate.return_value = {"error": "Geçersiz Token"}
    rv = client.post(
        "/add-to-cart",
        json={"product_id": "x"},
        headers={"Authorization": "Bearer bad"}
    )
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Geçersiz Token"

@patch("back.routes.routescart.validate_jwt")
def test_add_to_cart_expired_token(mock_validate, client):
    """
    ❌ Sepete ekleme: validate_jwt ‘Token süresi doldu’ dönerse 401 dönmeli
    """
    mock_validate.return_value = {"error": "Token süresi doldu"}
    rv = client.post(
        "/add-to-cart",
        json={"product_id": str(ObjectId())},
        headers={"Authorization": "Bearer expired"}
    )
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token süresi doldu"

@patch("back.routes.routescart.validate_jwt")
def test_add_to_cart_missing_product_id(mock_validate, client):
    """
    ❌ Sepete ekleme: JSON’da product_id yoksa 400 dönmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    rv = client.post(
        "/add-to-cart",
        json={},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 400
    assert rv.get_json()["error"] == "Ürün ID eksik!"

@patch("back.routes.routescart.validate_jwt")
def test_add_to_cart_invalid_objectid(mock_validate, client):
    """
    ❌ Sepete ekleme: Geçersiz ObjectId stringi 400 dönmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    rv = client.post(
        "/add-to-cart",
        json={"product_id": "nothex"},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 400
    assert rv.get_json()["error"] == "Geçersiz ürün ID!"

@patch("back.routes.routescart.validate_jwt")
@patch("back.routes.routescart.product_collection.find_one")
def test_add_to_cart_not_found(mock_find, mock_validate, client):
    """
    ❌ Sepete ekleme: product_collection.find_one None dönerse 404 dönmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    mock_find.return_value = None
    rv = client.post(
        "/add-to-cart",
        json={"product_id": str(ObjectId())},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 404
    assert rv.get_json()["error"] == "Ürün bulunamadı!"

# ---------- complete-cart endpoint tests ----------

@patch("back.routes.routescart.send_email_to_users")
@patch("back.routes.routescart.cart_collection.update_many")
@patch("back.routes.routescart.validate_jwt")
def test_complete_cart_success(
    mock_validate, mock_update, mock_send, client
):
    """
    ✅ Sepeti tamamlama: matched_count > 0 ise 200 dönmeli ve e-posta gönderilmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    # matched_count 2 örneği
    mock_update.return_value = MagicMock(matched_count=2)

    rv = client.post("/complete-cart", headers={"Authorization": "Bearer tok"})
    assert rv.status_code == 200
    assert "tamamlandı" in rv.get_json()["message"].lower()
    mock_update.assert_called_once_with(
        {"user_id": "u@e.com"}, {"$set": {"status": "Tamamlandı"}}
    )
    mock_send.assert_called_once_with("u@e.com", "Siparişiniz Alındı!")

def test_complete_cart_no_token(client):
    """
    ❌ Sepeti tamamlama: token header yoksa 401 dönmeli
    """
    rv = client.post("/complete-cart")
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token bulunamadı!"

@patch("back.routes.routescart.validate_jwt")
def test_complete_cart_invalid_token(mock_validate, client):
    """
    ❌ Sepeti tamamlama: validate_jwt error dönerse 401 dönmeli
    """
    mock_validate.return_value = {"error": "Geçersiz Token"}
    rv = client.post("/complete-cart", headers={"Authorization": "Bearer bad"})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Geçersiz Token"

@patch("back.routes.routescart.validate_jwt")
def test_complete_cart_expired_token(mock_validate, client):
    """
    ❌ Sepeti tamamlama: validate_jwt ‘Token süresi doldu’ dönerse 401 dönmeli
    """
    mock_validate.return_value = {"error": "Token süresi doldu"}
    rv = client.post("/complete-cart", headers={"Authorization": "Bearer expired"})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token süresi doldu"

@patch("back.routes.routescart.validate_jwt")
@patch("back.routes.routescart.cart_collection.update_many")
def test_complete_cart_empty(mock_update, mock_validate, client):
    """
    ❌ Sepet boşsa matched_count == 0 → 400 dönmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    mock_update.return_value = MagicMock(matched_count=0)

    rv = client.post("/complete-cart", headers={"Authorization": "Bearer tok"})
    assert rv.status_code == 400
    assert rv.get_json()["error"] == "Sepetinizde tamamlanacak ürün yok!"

# ---------- get-cart endpoint tests ----------

@patch("back.routes.routescart.product_collection.find_one")
@patch("back.routes.routescart.cart_collection.find")
@patch("back.routes.routescart.validate_jwt")
def test_get_cart_success_with_items(
    mock_validate, mock_find, mock_prod_find, client
):
    """
    ✅ Sepet görüntüleme: geçerli token, ürün bulunur → cart listesi dönmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    oid = ObjectId()
    mock_find.return_value = [{
        "_id": oid, "product_id": oid, "quantity": 2
    }]
    mock_prod_find.return_value = {
        "_id": oid, "product_name": "PN", "price": 5
    }

    rv = client.get("/get-cart", headers={"Authorization": "Bearer tok"})
    assert rv.status_code == 200
    cart = rv.get_json()["cart"]
    assert len(cart) == 1
    assert cart[0]["product_name"] == "PN"
    assert cart[0]["quantity"] == 2

@patch("back.routes.routescart.cart_collection.find")
@patch("back.routes.routescart.validate_jwt")
def test_get_cart_skip_invalid_items(mock_validate, mock_find, client):
    """
    ✅ Sepet görüntüleme: invalid product_id atlanır, boş liste döner
    """
    mock_validate.return_value = {"email": "u@e.com"}
    mock_find.return_value = [{
        "_id": "x", "product_id": "x", "quantity": 1
    }]

    rv = client.get("/get-cart", headers={"Authorization": "Bearer tok"})
    assert rv.status_code == 200
    assert rv.get_json()["cart"] == []

def test_get_cart_no_token(client):
    """
    ❌ Sepet görüntüleme: token header yoksa 401 dönmeli
    """
    rv = client.get("/get-cart")
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token bulunamadı!"

@patch("back.routes.routescart.validate_jwt")
def test_get_cart_invalid_token(mock_validate, client):
    """
    ❌ Sepet görüntüleme: validate_jwt error dönerse 401 dönmeli
    """
    mock_validate.return_value = {"error": "Geçersiz Token"}
    rv = client.get("/get-cart", headers={"Authorization": "Bearer bad"})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Geçersiz Token"

@patch("back.routes.routescart.validate_jwt")
def test_get_cart_expired_token(mock_validate, client):
    """
    ❌ Sepet görüntüleme: validate_jwt ‘Token süresi doldu’ dönerse 401 dönmeli
    """
    mock_validate.return_value = {"error": "Token süresi doldu"}
    rv = client.get("/get-cart", headers={"Authorization": "Bearer expired"})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token süresi doldu"

# ---------- delete-from-cart endpoint tests ----------

@patch("back.routes.routescart.cart_collection.delete_one")
@patch("back.routes.routescart.validate_jwt")
def test_delete_from_cart_success(mock_validate, mock_delete, client):
    """
    ✅ Sepetten silme: matched_count=1 ise 200 dönmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    mock_delete.return_value = MagicMock(deleted_count=1)

    rv = client.post(
        "/delete-from-cart",
        json={"product_id": str(ObjectId())},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 200
    assert rv.get_json()["message"] == "Ürün sepetten çıkarıldı!"
    mock_delete.assert_called_once()

def test_delete_from_cart_no_token(client):
    """
    ❌ Sepetten silme: token header yoksa 401 dönmeli
    """
    rv = client.post("/delete-from-cart", json={"product_id": "x"})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token bulunamadı!"

@patch("back.routes.routescart.validate_jwt")
def test_delete_from_cart_invalid_token(mock_validate, client):
    """
    ❌ Sepetten silme: validate_jwt error dönerse 401 dönmeli
    """
    mock_validate.return_value = {"error": "Geçersiz Token"}
    rv = client.post(
        "/delete-from-cart",
        json={"product_id": str(ObjectId())},
        headers={"Authorization": "Bearer bad"}
    )
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Geçersiz Token"

@patch("back.routes.routescart.validate_jwt")
def test_delete_from_cart_expired_token(mock_validate, client):
    """
    ❌ Sepetten silme: validate_jwt ‘Token süresi doldu’ dönerse 401 dönmeli
    """
    mock_validate.return_value = {"error": "Token süresi doldu"}
    rv = client.post(
        "/delete-from-cart",
        json={"product_id": str(ObjectId())},
        headers={"Authorization": "Bearer expired"}
    )
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token süresi doldu"

@patch("back.routes.routescart.validate_jwt")
def test_delete_from_cart_missing_product_id(mock_validate, client):
    """
    ❌ Sepetten silme: product_id eksikse 400 dönmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    rv = client.post("/delete-from-cart", json={}, headers={"Authorization": "Bearer tok"})
    assert rv.status_code == 400
    assert rv.get_json()["error"] == "Ürün ID'si eksik!"

@patch("back.routes.routescart.validate_jwt")
def test_delete_from_cart_invalid_objectid(mock_validate, client):
    """
    ❌ Sepetten silme: geçersiz ObjectId stringi 400 dönmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    rv = client.post(
        "/delete-from-cart",
        json={"product_id": "nothex"},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 400
    assert rv.get_json()["error"] == "Geçersiz ürün ID!"

@patch("back.routes.routescart.validate_jwt")
@patch("back.routes.routescart.cart_collection.delete_one")
def test_delete_from_cart_not_found(mock_delete, mock_validate, client):
    """
    ❌ Sepetten silme: matched_count=0 ise 404 dönmeli
    """
    mock_validate.return_value = {"email": "u@e.com"}
    mock_delete.return_value = MagicMock(deleted_count=0)

    rv = client.post(
        "/delete-from-cart",
        json={"product_id": str(ObjectId())},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 404
    assert rv.get_json()["error"] == "Ürün sepette bulunamadı."


    # cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
    # pytest testler/test_routescart.py