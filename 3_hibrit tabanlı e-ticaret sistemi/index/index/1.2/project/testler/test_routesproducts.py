# testler/test_routesproducts.py

import sys
import os
import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId

# Proje kök dizinini path’e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from back.routes.routesproducts import products_bp

@pytest.fixture
def app():
    """Flask uygulamasını oluştur ve products blueprint’ini kaydet."""
    app = Flask(__name__)
    app.register_blueprint(products_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Flask test client’ını dönder."""
    return app.test_client()

# ---------- add-product ----------

@patch("back.routes.routesproducts.product_collection.insert_one")
@patch("back.routes.routesproducts.validate_jwt")
def test_add_product_success(mock_validate, mock_insert, client):
    """✅ supplier rolüyle geçerli body → 201 & insert_one çağrılsın"""
    mock_validate.return_value = {"email": "sup@e.com", "role": "supplier"}

    rv = client.post(
        "/add-product",
        json={"product_name": "Laptop", "price": 1500},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 201
    assert rv.get_json()["message"] == "Ürün başarıyla eklendi!"
    mock_insert.assert_called_once_with({
        "product_name": "Laptop",
        "price": 1500,
        "added_by": "sup@e.com"
    })

def test_add_product_no_token(client):
    """❌ Authorization header yok → 401"""
    rv = client.post("/add-product", json={"product_name": "X", "price": 1})
    assert rv.status_code == 401
    assert rv.get_json()["error"] == "Token bulunamadı!"

@patch("back.routes.routesproducts.validate_jwt")
def test_add_product_invalid_token(mock_validate, client):
    """❌ validate_jwt hata döner → 401"""
    mock_validate.return_value = {"error": "Geçersiz Token"}
    rv = client.post(
        "/add-product",
        json={"product_name": "X", "price": 1},
        headers={"Authorization": "Bearer bad"}
    )
    assert rv.status_code == 401

@patch("back.routes.routesproducts.validate_jwt")
def test_add_product_expired_token(mock_validate, client):
    """❌ token süresi doldu → 401"""
    mock_validate.return_value = {"error": "Token süresi doldu"}
    rv = client.post(
        "/add-product",
        json={"product_name": "X", "price": 1},
        headers={"Authorization": "Bearer expired"}
    )
    assert rv.status_code == 401

@patch("back.routes.routesproducts.validate_jwt")
def test_add_product_non_supplier(mock_validate, client):
    """❌ role != supplier → 403"""
    mock_validate.return_value = {"email": "u@e.com", "role": "customer"}
    rv = client.post(
        "/add-product",
        json={"product_name": "X", "price": 1},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 403

@patch("back.routes.routesproducts.validate_jwt")
def test_add_product_missing_fields(mock_validate, client):
    """❌ product_name veya price eksik → 400"""
    mock_validate.return_value = {"email": "sup@e.com", "role": "supplier"}
    # Eksik product_name
    rv1 = client.post(
        "/add-product",
        json={"price": 100},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv1.status_code == 400
    # Eksik price
    rv2 = client.post(
        "/add-product",
        json={"product_name": "X"},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv2.status_code == 400

# ---------- update-product ----------

@patch("back.routes.routesproducts.product_collection.update_one")
@patch("back.routes.routesproducts.validate_jwt")
def test_update_product_success(mock_validate, mock_update, client):
    """✅ supplier & geçerli id/body → 200"""
    mock_validate.return_value = {"email": "sup@e.com", "role": "supplier"}
    mock_update.return_value = MagicMock(modified_count=1)

    pid = str(ObjectId())
    rv = client.put(
        f"/update-product/{pid}",
        json={"product_name": "Tablet", "price": 800},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 200

@patch("back.routes.routesproducts.validate_jwt")
def test_update_product_no_token(mock_validate, client):
    """❌ token yok → 401"""
    pid = str(ObjectId())
    rv = client.put(f"/update-product/{pid}", json={"product_name": "X", "price": 1})
    assert rv.status_code == 401

@patch("back.routes.routesproducts.validate_jwt")
def test_update_product_invalid_token(mock_validate, client):
    """❌ geçersiz token → 401"""
    mock_validate.return_value = {"error": "Geçersiz Token"}
    pid = str(ObjectId())
    rv = client.put(
        f"/update-product/{pid}",
        json={"product_name": "X", "price": 1},
        headers={"Authorization": "Bearer bad"}
    )
    assert rv.status_code == 401

@patch("back.routes.routesproducts.validate_jwt")
def test_update_product_expired_token(mock_validate, client):
    """❌ token süresi doldu → 401"""
    mock_validate.return_value = {"error": "Token süresi doldu"}
    pid = str(ObjectId())
    rv = client.put(
        f"/update-product/{pid}",
        json={"product_name": "X", "price": 1},
        headers={"Authorization": "Bearer expired"}
    )
    assert rv.status_code == 401

@patch("back.routes.routesproducts.validate_jwt")
def test_update_product_non_supplier(mock_validate, client):
    """❌ customer role → 403"""
    mock_validate.return_value = {"email": "u@e.com", "role": "customer"}
    pid = str(ObjectId())
    rv = client.put(
        f"/update-product/{pid}",
        json={"product_name": "X", "price": 1},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 403

@patch("back.routes.routesproducts.validate_jwt")
def test_update_product_invalid_id(mock_validate, client):
    """❌ invalid ObjectId → 400"""
    mock_validate.return_value = {"email": "sup@e.com", "role": "supplier"}
    rv = client.put(
        "/update-product/nothex",
        json={"product_name": "X", "price": 1},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 400

@patch("back.routes.routesproducts.validate_jwt")
def test_update_product_missing_fields(mock_validate, client):
    """❌ eksik name/price → 400"""
    mock_validate.return_value = {"email": "sup@e.com", "role": "supplier"}
    pid = str(ObjectId())
    # eksik name
    rv1 = client.put(
        f"/update-product/{pid}",
        json={"price": 10},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv1.status_code == 400
    # eksik price
    rv2 = client.put(
        f"/update-product/{pid}",
        json={"product_name": "X"},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv2.status_code == 400

@patch("back.routes.routesproducts.product_collection.update_one")
@patch("back.routes.routesproducts.validate_jwt")
def test_update_product_not_found(mock_validate, mock_update, client):
    """❌ modified_count=0 → 404"""
    mock_validate.return_value = {"email": "sup@e.com", "role": "supplier"}
    mock_update.return_value = MagicMock(modified_count=0)

    pid = str(ObjectId())
    rv = client.put(
        f"/update-product/{pid}",
        json={"product_name": "X", "price": 1},
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 404

# ---------- delete-product ----------

@patch("back.routes.routesproducts.product_collection.update_one")
@patch("back.routes.routesproducts.validate_jwt")
def test_delete_product_success(mock_validate, mock_update, client):
    """✅ supplier ile valid id → 200"""
    mock_validate.return_value = {"email": "sup@e.com", "role": "supplier"}
    mock_update.return_value = MagicMock(modified_count=1)

    pid = str(ObjectId())
    rv = client.delete(
        f"/delete-product/{pid}",
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 200

@patch("back.routes.routesproducts.validate_jwt")
def test_delete_product_no_token(mock_validate, client):
    """❌ token yok → 401"""
    pid = str(ObjectId())
    rv = client.delete(f"/delete-product/{pid}")
    assert rv.status_code == 401

@patch("back.routes.routesproducts.validate_jwt")
def test_delete_product_invalid_token(mock_validate, client):
    """❌ geçersiz token → 401"""
    mock_validate.return_value = {"error": "Geçersiz Token"}
    pid = str(ObjectId())
    rv = client.delete(
        f"/delete-product/{pid}",
        headers={"Authorization": "Bearer bad"}
    )
    assert rv.status_code == 401

@patch("back.routes.routesproducts.validate_jwt")
def test_delete_product_expired_token(mock_validate, client):
    """❌ token süresi doldu → 401"""
    mock_validate.return_value = {"error": "Token süresi doldu"}
    pid = str(ObjectId())
    rv = client.delete(
        f"/delete-product/{pid}",
        headers={"Authorization": "Bearer expired"}
    )
    assert rv.status_code == 401

@patch("back.routes.routesproducts.validate_jwt")
def test_delete_product_non_supplier(mock_validate, client):
    """❌ customer role → 403"""
    mock_validate.return_value = {"email": "u@e.com", "role": "customer"}
    pid = str(ObjectId())
    rv = client.delete(
        f"/delete-product/{pid}",
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 403

@patch("back.routes.routesproducts.validate_jwt")
def test_delete_product_invalid_id(mock_validate, client):
    """❌ invalid ObjectId → 400"""
    mock_validate.return_value = {"email": "sup@e.com", "role": "supplier"}
    rv = client.delete(
        "/delete-product/nothex",
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 400

@patch("back.routes.routesproducts.product_collection.update_one")
@patch("back.routes.routesproducts.validate_jwt")
def test_delete_product_not_found(mock_validate, mock_update, client):
    """❌ modified_count=0 → 404"""
    mock_validate.return_value = {"email": "sup@e.com", "role": "supplier"}
    mock_update.return_value = MagicMock(modified_count=0)

    pid = str(ObjectId())
    rv = client.delete(
        f"/delete-product/{pid}",
        headers={"Authorization": "Bearer tok"}
    )
    assert rv.status_code == 404


    #  cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
    #  pytest testler/test_routesproducts.py