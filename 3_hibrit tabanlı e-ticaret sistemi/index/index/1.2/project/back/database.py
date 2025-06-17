#from flask_mysqldb import MySQL
from pymongo import MongoClient
from back.config import MYSQL_CONFIG, MONGO_CONFIG
from flask_mysqldb import MySQL  # Doğru sınıf adı MySQL



mysql = MySQL()
mongo_client = MongoClient(MONGO_CONFIG["url"])
mongo_db = mongo_client[MONGO_CONFIG["db_name"]]
cart_collection = mongo_db["carts"]
product_collection = mongo_db["products"]

def init_db(app):
    # Flask app config ayarlarını doğru bir şekilde yapıyoruz
    app.config['MYSQL_HOST'] = MYSQL_CONFIG["host"]
    app.config['MYSQL_USER'] = MYSQL_CONFIG["user"]  # root kullanıcısı
    app.config['MYSQL_PASSWORD'] = MYSQL_CONFIG["password"]
    app.config['MYSQL_DB'] = MYSQL_CONFIG["db"]
    
    # MySQL bağlatısını başlat
    mysql.init_app(app)
