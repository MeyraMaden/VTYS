#!/usr/bin/env python3
import subprocess
import sys

# 1) Önce testleri çalıştır
print("🔍 Birim testleri çalıştırılıyor…")
res = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "testler"],
    capture_output=False
)
if res.returncode != 0:
    print(f"❌ {res.returncode} hata(lar) bulundu, uygulama başlatılmıyor.")
    sys.exit(res.returncode)

# 2) Testler geçtikten sonra uygulamayı başlat
print("✅ Tüm testler başarılı. Uygulama başlatılıyor…")
from app import app  # eğer sizin entry-point’iniz farklıysa ona göre düzeltin
app.run(host="0.0.0.0", port=5000, debug=True)


#   cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
#    python run.py