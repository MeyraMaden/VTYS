
#  Hibrit Veritabanı ile E-Ticaret API Projesi

Bu proje, **MySQL** ve **MongoDB** veritabanlarını birlikte kullanarak geliştirilmiş bir e-ticaret sistemidir. Kullanıcılar JWT ile kimlik doğrulaması yaparak ürün ekleyebilir, sepet yönetimi gerçekleştirebilir ve sipariş verebilir. Aynı zamanda e-posta bildirimleri ve şifre sıfırlama özelliklerini de içerir.

##  Kullanılan Teknolojiler

- **Python (Flask Framework)**
- **MySQL** – Kullanıcı yönetimi ve kimlik doğrulama
- **MongoDB** – Sepet ve ürün yönetimi
- **JWT (JSON Web Tokens)** – Güvenli oturum yönetimi
- **bcrypt** – Şifreleme
- **SMTP (Gmail)** – E-posta bildirim sistemi

##  Proje Özellikleri

| Özellik | Açıklama |
|--------|----------|
|  Kullanıcı Kayıt & Giriş | MySQL üzerinden kayıt ve login |
|  JWT Authentication | Login sonrası token ile korumalı endpoint’lere erişim |
|  Rol Sistemi | "customer" ve "supplier" rolleri ile yetkilendirme |
|  Sepet Yönetimi | Ürün ekleme, listeleme, tamamlama (MongoDB) |
|  Ürün Yönetimi | Tedarikçiler için ürün ekleme, güncelleme, soft-delete |
|  E-posta Bildirimleri | Sepet güncelleme ve sipariş tamamlama bildirimleri |
|  Şifremi Unuttum | Token ile şifre sıfırlama bağlantısı gönderimi |
|  Profil Güncelleme | E-posta ve şifre değiştirme (MySQL) |


## ▶️ Kurulum ve Çalıştırma
Python 3.8 veya üzeri

MySQL Server

MongoDB (local ya da bulut tabanlı)

pip (Python paket yöneticisi)

### 1. Gerekli Kütüphaneleri Kur

```bash
pip install -r requirements.txt
```

### 2. MySQL Veritabanı Oluştur

```sql
CREATE DATABASE ecommerce_db;
USE ecommerce_db;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL
);
```

### 3. MongoDB Veritabanı

MongoDB'de `ecommerce_db` isimli bir veritabanı otomatik oluşturulur. Koleksiyonlar: `products`, `carts`.

### 4. Gmail SMTP Ayarları

Google Hesabınızdan uygulama şifresi oluşturun ve `app.py` içinde ilgili yere ekleyin:

```python
sender_email = "youremail@gmail.com"
sender_password = "uygulama_sifresi"
```

### 5. Uygulamayı Başlat

```bash
python app.py
```

##  Örnek Kullanım

- Authorization: Bearer `<JWT_TOKEN>` şeklinde header ile korumalı endpoint'lere erişin.
- Postman koleksiyonu ile test için örnek istekler hazırlanacaktır.

##  API Endpoint'leri (Kısa Liste)

| Endpoint | Açıklama |
|---------|----------|
| POST /register | Kullanıcı kaydı |
| POST /login | Giriş ve JWT alma |
| GET /profile | Kullanıcı profili görüntüleme |
| POST /add-product | Ürün ekleme (supplier) |
| POST /add-to-cart | Sepete ürün ekleme |
| GET /get-cart | Sepeti görüntüleme |
| POST /complete-cart | Sipariş tamamlama |
| PUT /update-product/:id | Ürün güncelleme |
| DELETE /delete-product/:id | Ürün silme |
| POST /forgot-password | Şifre sıfırlama talebi |
| POST /reset-password | Şifre güncelleme |
| PUT /update-profile | Kullanıcı bilgisi güncelleme |

##  Notlar

- Tüm JWT kontrollü endpoint’ler Authorization header’ı ister.
- Tedarikçi dışındaki kullanıcılar ürün ekleyemez veya silemez.
- MongoDB ObjectId kullanılırken `ObjectId(product_id)` gibi kullanılmalıdır.



Hazırlayanlar: **[Helin Bağlamış,Hümeyra Hasmaden]**  
Ders: VTYS – Bilgisayar Mühendisliği  
Danışman: **DR. HAKAN AYDIN**
