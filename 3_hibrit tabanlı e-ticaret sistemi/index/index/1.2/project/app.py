from flask import Flask, redirect
from back.database import init_db
from back.routes.routesusers import users_bp
from back.routes.routesproducts import products_bp
from back.routes.routescart import cart_bp
from flask_cors import CORS

app = Flask(
  __name__,
  static_folder='front',      # front klasöründeki dosyaları /<dosya> yolu ile sunar
  static_url_path=''          # URL kökünde statik dosyaları yayımlamak için
)
CORS(app)
app.secret_key = 'çok-gizli-bir-anahtar'

# Anasayfa doğrudan login’e gönderilsin
@app.route('/')
def index():
    return redirect('/login')

# Database & API blueprints
init_db(app)
app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
app.register_blueprint(cart_bp)



if __name__ == '__main__':
    app.run(debug=True)




'''cd "C:/Users/lenovo/OneDrive/Resimler/Masaüstü/yazılım sınama/project"
python -m back.app'''
   # "C:\Users\lenovo\OneDrive\Resimler\Masaüstü\yazılım sınama\project"