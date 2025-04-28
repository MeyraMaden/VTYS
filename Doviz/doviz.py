from influxdb_client import InfluxDBClient, Point, WritePrecision
import requests
import time

# InfluxDB bağlantı bilgileri
url = "http://localhost:8086"  # InfluxDB'nin adresi
token = "OJ1-3LkuY6VqGet9KF76susVha8I_U580vs0e7R-LbZc5l6ktTwQQ7uJBOrL2wpkmBOqlPlQIeLEeYszngKoxw=="  # Token
org = "yuki"  # Organizasyon adı
bucket = "influxBucket"  # Bucket adı

# API key
api_key = "82e8169f01-341574e0f1-svfxye"

# API URL
forex_url = f"https://api.fastforex.io/fetch-one?from=EUR&to=TRY&api_key={api_key}"

# InfluxDB bağlantısını başlat
client = InfluxDBClient(url=url, token=token)
write_api = client.write_api()

# Döviz kuru verisini almak ve InfluxDB'ye yazmak
def write_data():
    response = requests.get(forex_url)

    # Eğer API'den başarılı bir yanıt alınamazsa, hata mesajı ver
    if response.status_code != 200:
        print(f"Hata: API'den veri alınamadı. Durum Kodu: {response.status_code}")
        return
    
    data = response.json()

    # API'den alınan veriyi kontrol et
    if "result" in data and "TRY" in data["result"]:
        euro_to_try = data["result"]["TRY"]

    
        # Zaman damgası, milisaniye cinsinden
        timestamp = int(time.time() * 1000)  # time.time() saniye , milisaniye için * 1000 yapılır

        # InfluxDB'ye veri ekleme
        point = Point("forex_rate") \
            .tag("currency_pair", "EUR/TRY") \
            .field("rate", euro_to_try) \
            .time(timestamp, WritePrecision.MS)  # MS milisaniye

        try:
            # Veriyi InfluxDB'ye yaz
            write_api.write(bucket=bucket, org=org, record=point)
            print(f"Veri InfluxDB'ye kaydedildi: 1 Euro = {euro_to_try} TRY")
        except Exception as e:
                print(f"Veri yazılırken hata oluştu: {e}")
    else:
            print("API'den alınan veriler geçersiz.")

                
# Sürekli veri alıp kaydetme
while True:
    write_data()
    time.sleep(30) # 30 saniye