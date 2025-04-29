# Token Tabanlı Kimlik Doğrulama API'si (Spring Boot + JWT)

Bu proje, Spring Boot kullanılarak geliştirilmiş basit bir JWT (JSON Web Token) tabanlı kimlik doğrulama sistemidir. Kullanıcılar kayıt olabilir, giriş yaparak token alabilir ve bu token'ı doğrulatabilir. Proje eğitim amaçlıdır ve geçici bellekte kullanıcı verisi tutar. Veritabanı entegrasyonu yoktur.

## 📁 Proje Yapısı

- model/User.java: Kullanıcı bilgilerini tutan model sınıfı  
- util/JwtUtil.java: JWT oluşturma, doğrulama ve çözümleme işlemlerini içerir  
- controller/AuthController.java: Kayıt, giriş ve token doğrulama işlemleri için API endpoint'lerini içerir  

## 🚀 Özellikler

- Kullanıcı kaydı (POST /api/register)  
- Giriş yaparak token alma (POST /api/login)  
- Token doğrulama (POST /api/validate)  
- JWT içinde e-posta bilgisi taşınır  
- Postman ile test edilebilir  

## 🔧 Kullanılan Teknolojiler

- Java 17+  
- Spring Boot  
- JWT (jjwt kütüphanesi)  
- Postman  

## 🛠️ Kurulum ve Çalıştırma

### 1. Projeyi Klonlayın

git clone https://github.com/MeyraMaden/VTYS/tree/meyra/1_token/token.git  
cd token

### 2. Uygulamayı Başlatın

IDE (IntelliJ, Eclipse vb.) veya terminal üzerinden çalıştırabilirsiniz:  
./mvnw spring-boot:run

## 🔐 API Kullanımı ve Test (Postman)

### 1. Kayıt (Register)

POST /api/register  
JSON Body:  
{
  "name": "meyra",
  "surname": "helin",
  "email": "melin@example.com",
  "password": "1234"
}

### 2. Giriş ve Token Alma (Login)

POST /api/login  
JSON Body:  
{
  "email": "melin@example.com",
  "password": "1234"
}  
Başarılı giriş durumunda JWT Token döner:  
eyJhbGciOiJIUzI1NiJ9...

### 3. Token Doğrulama

POST /api/validate  
JSON Body:  
{
  "token": "eyJhbGciOiJIUzI1NiJ9..."
}

## ℹ️ Notlar

- Token süresi sadece 1 dakikadır. Test amaçlı kısa tutulmuştur.  
- secretKey sabit bir değerdir. Gerçek projelerde .env dosyasından veya güvenli bir yapılandırmadan alınmalıdır.  
- Uygulama geçici bellekte kullanıcıları tutar. Veritabanı entegrasyonu yoktur.  
- Şifreler şifrelenmeden tutulur. Gerçek projelerde kesinlikle BCrypt gibi algoritmalar kullanılmalıdır.  

## 📄 Lisans

Bu proje eğitim amaçlıdır. Ticari kullanım önerilmez.