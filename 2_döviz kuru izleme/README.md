# 💱 Döviz Kuru İzleme Sistemi (EUR/TRY)

Bu proje, Python ile FastForex API üzerinden alınan EUR/TRY döviz kuru verilerini belirli aralıklarla InfluxDB'ye kaydeder ve Grafana ile görselleştirir.

## 🚀 Kullanılan Teknolojiler
- Python – Veri çekme ve kaydetme
- FastForex API – Gerçek zamanlı döviz kuru verisi
- InfluxDB – Zaman serisi veritabanı
- Grafana – Veri görselleştirme aracı

## ⚙️ Kurulum ve Çalıştırma

1. Gerekli kütüphaneleri yükleyin:
   pip install influxdb-client requests

2. `main.py` dosyasında aşağıdaki alanları kendi bilgilerinizle doldurun:
   - token → InfluxDB token
   - org → InfluxDB organizasyon adı
   - bucket → InfluxDB bucket adı
   - api_key → FastForex API anahtarı

3. InfluxDB ve Grafana'yı kurun:
   - [InfluxDB](https://www.influxdata.com/) ve [Grafana](https://grafana.com/) sitelerinden indirip kurun
   - InfluxDB'de bir bucket ve token oluşturun
   - Grafana’yı http://localhost:3000 adresinden açın

4. Grafana’da InfluxDB bağlantısını yapın:
   - Data Sources → Add data source → InfluxDB
   - URL: http://localhost:8086
   - Token, Organization ve Bucket bilgilerini girin
   - Save & Test ile bağlantıyı doğrulayın

5. Script’i çalıştırın:
   python main.py

Her 30 saniyede bir EUR/TRY kuru çekilir ve InfluxDB’ye yazılır.

## 📊 Grafana Dashboard Oluşturma

Aşağıdaki Flux sorgusunu kullanarak döviz verilerini zaman çizelgesi olarak görselleştirebilirsiniz:

   from(bucket: "influxBucket")
     |> range(start: -1h)
     |> filter(fn: (r) => r._measurement == "forex_rate")
     |> filter(fn: (r) => r._field == "rate")

## 📌 Notlar
- FastForex API ücretsiz planda sınırlı kullanım sunar.
- InfluxDB ve Grafana arka planda çalışıyor olmalıdır.

## 🪪 Lisans

Bu proje eğitim amaçlıdır. Ticari kullanıma uygun değildir.