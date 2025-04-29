# Firebase ile Android Kullanıcı Giriş ve Kayıt Sistemi

Bu proje, Firebase Authentication kullanarak Android üzerinde e-posta ve şifre ile kullanıcı *kayıt* ve *giriş* işlemlerini gerçekleştirmektedir.

## 🚀 Özellikler

- Firebase Authentication ile kullanıcı kaydı
- Firebase ile giriş işlemi
- Giriş/Kayıt sonrası kullanıcı bilgilerini Intent ile ikinci aktiviteye aktarma
- Firebase ile oturum yönetimi

## 🛠 Gereksinimler

- Android Studio (Arctic Fox veya üzeri)
- Firebase projesi
- Minimum SDK: 21 (Android 5.0)

## 🔧 Firebase Kurulumu

1. [Firebase Console](https://console.firebase.google.com/) üzerinden yeni bir proje oluştur.
2. Projeye bir Android uygulaması ekle.
3. google-services.json dosyasını indir ve app/ klasörüne yerleştir.
4. build.gradle (Project) ve build.gradle (Module) dosyalarını Firebase yönergelerine göre düzenle.
5. Sync işlemini tamamla.

## 🧪 Uygulama Kullanımı

### 🔐 Kayıt Ol

- E-posta ve şifre ile kayıt olmak için "Kayıt Ol" butonuna basılır.
- Firebase'de kullanıcı oluşturulur.
- Kayıt sonrası bilgiler SecondActivity'ye aktarılır.

### 🔐 Giriş Yap

- Daha önce kayıt olmuş kullanıcı, e-posta ve şifre ile giriş yapabilir.
- Giriş sonrası bilgiler SecondActivity'ye aktarılır.

## 📂 Kod Yapısı

- MainActivity.java → Giriş ve kayıt işlemleri, Firebase bağlantısı
- SecondActivity.java → Giriş sonrası yönlendirilen ekran
- activity_main.xml → E-posta, şifre giriş alanları ve butonlar
- activity_second.xml → Hoş geldin ekranı 

## 🧾 Notlar

- E-posta doğrulama (isEmailVerified) hazır, ancak e-posta doğrulama maili gönderme kodu henüz eklenmemiştir. (Eklenebilir)
- Şu anda kullanıcı bilgileri sadece Intent ile aktarılmakta ve cihazda tutulmamaktadır.
- Uygulama tek aktivite üzerinden çalışmakta, daha fazla güvenlik veya kullanıcı deneyimi için SharedPreferences, ViewModel, Firebase Firestore vb. entegre edilebilir.

## 🪪 Lisans

Bu proje eğitim amaçlıdır. Ticari kullanıma uygun değildir.