# testler/test_database.py

import pytest
import sys
import os
from flask import Flask
from pymongo.collection import Collection
from unittest.mock import MagicMock

# Proje kökünü path’e ekle ki back paketi import edilebilsin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import back.database as db
from back.database import init_db, mysql, cart_collection, product_collection, mongo_client
from flask_mysqldb import MySQL
from back.config import MYSQL_CONFIG

@pytest.fixture
def app():
    """Basit bir Flask uygulaması oluşturur."""
    return Flask(__name__)



def test_init_db_sets_config_and_calls_init_app(monkeypatch, app):
    """
    ✅ init_db:
      - app.config içindeki MYSQL_* ayarları MYSQL_CONFIG ile eşleşmeli
      - mysql.init_app(app) bir kez çağrılmalı
    """
    # mysql.init_app’i mock’la
    mock_init = MagicMock()
    monkeypatch.setattr(db.mysql, 'init_app', mock_init)

    init_db(app)

    # host/user/pass/db kontrolleri
    assert app.config['MYSQL_HOST']     == MYSQL_CONFIG["host"]
    assert app.config['MYSQL_USER']     == MYSQL_CONFIG["user"]
    assert app.config['MYSQL_PASSWORD'] == MYSQL_CONFIG["password"]
    assert app.config['MYSQL_DB']       == MYSQL_CONFIG["db"]

    # init_app gerçekten çağrıldı mı?
    mock_init.assert_called_once_with(app)


def test_mysql_connect_success(monkeypatch, app):
    """
    ✅ mysql.connect():
      - mock’ladığımız dummy_conn’u döndürmeli
    """
    init_db(app)
    dummy_conn = object()

    # connect bir @property, sınıf üzerinde override ediyoruz
    monkeypatch.setattr(MySQL, 'connect', lambda self: dummy_conn)

    conn = db.mysql.connect()
    assert conn is dummy_conn


def test_mysql_connect_failure(monkeypatch, app):
    """
    ⚠ mysql.connect():
      - Hata fırlatıldığında exception propagate edilmeli
    """
    init_db(app)

    def fake_connect(self):
        raise Exception("MySQL bağlantı hatası")
    monkeypatch.setattr(MySQL, 'connect', fake_connect)

    with pytest.raises(Exception) as exc:
        _ = db.mysql.connect()

    assert "MySQL bağlantı hatası" in str(exc.value)


def test_mongo_ping_success(monkeypatch):
    """
    ✅ mongo_client.admin.command('ping'):
      - {'ok': 1} dönmeli
    """
    fake_admin = MagicMock()
    fake_admin.command.return_value = {"ok": 1}
    monkeypatch.setattr(mongo_client, 'admin', fake_admin)

    result = mongo_client.admin.command("ping")
    fake_admin.command.assert_called_once_with("ping")
    assert result == {"ok": 1}


def test_mongo_ping_failure(monkeypatch):
    """
    ⚠ mongo_client.admin.command('ping'):
      - Hata fırlatıldığında exception yükselmeli
    """
    fake_admin = MagicMock()
    fake_admin.command.side_effect = Exception("MongoDB bağlantı hatası")
    monkeypatch.setattr(mongo_client, 'admin', fake_admin)

    with pytest.raises(Exception) as exc:
        mongo_client.admin.command("ping")

    fake_admin.command.assert_called_once_with("ping")
    assert "MongoDB bağlantı hatası" in str(exc.value)


def test_cart_collection_type_and_name():
    """
    ✅ cart_collection:
      - pymongo.collection.Collection tipinde
      - name == 'carts'
    """
    assert isinstance(cart_collection, Collection)
    assert cart_collection.name == "carts"


def test_product_collection_type_and_name():
    """
    ✅ product_collection:
      - pymongo.collection.Collection tipinde
      - name == 'products'
    """
    assert isinstance(product_collection, Collection)
    assert product_collection.name == "products"


    # cd "C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project"
    #  pytest testler/test_database.py