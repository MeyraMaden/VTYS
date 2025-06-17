import unittest
import time
from unittest.mock import patch
import jwt

from back.config import SECRET_KEY
from back.auth import generate_jwt, validate_jwt

class CustomTestResult(unittest.TextTestResult):
    """Test sonuçlarını sözel olarak yazdıran özel sınıf."""
    def addSuccess(self, test):
        super().addSuccess(test)
        print(f"✅ Test Başarılı: {test._testMethodName} → {test.shortDescription()}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"❌ Test Başarısız: {test._testMethodName} → {test.shortDescription()}")

    def addError(self, test, err):
        super().addError(test, err)
        print(f"⚠ Test Hata Verdi: {test._testMethodName} → {test.shortDescription()}")

class TestAuth(unittest.TestCase):
    """auth.py içindeki JWT oluşturma ve doğrulama fonksiyonlarının tüm durum testleri."""

    def test_generate_jwt_not_empty(self):
        """Token boş mu?"""
        token = generate_jwt("a@b.com", "user")
        # Üretilen token None veya boş string olmamalı
        self.assertTrue(token, "generate_jwt boş bir değer döndürdü")

    def test_generate_jwt_payload_fields(self):
        """Token içinde email, role, iat ve exp alanları var mı?"""
        token = generate_jwt("a@b.com", "user")
        # verify_exp=False ile expiration kontrolünü pas geçiyoruz
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        # Payload alanlarını doğrula
        self.assertEqual(decoded["email"], "a@b.com")
        self.assertEqual(decoded["role"], "user")
        self.assertIn("iat", decoded)
        self.assertIn("exp", decoded)

    def test_generate_jwt_default_expiration(self):
        """Varsayılan expiration 7 gün mü? (±1s tolerans)"""
        expected = 7 * 24 * 60 * 60
        token = generate_jwt("a@b.com", "user")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        delta = decoded["exp"] - decoded["iat"]
        # Bir saniyelik tolerans kabul et
        self.assertAlmostEqual(delta, expected, delta=1,
            msg=f"Beklenen ~{expected}s, bulunan {delta}s")

    def test_generate_jwt_custom_expiration(self):
        """Parametre ile verilen expiration değeri geçerli mi? (60s, ±1s)"""
        custom = 60
        token = generate_jwt("a@b.com", "user", expiration=custom)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        delta = decoded["exp"] - decoded["iat"]
        self.assertAlmostEqual(delta, custom, delta=1,
            msg=f"Beklenen ~{custom}s, bulunan {delta}s")

    @patch("back.auth.jwt.encode")
    def test_generate_jwt_encode_exception(self, mock_encode):
        """jwt.encode hata fırlatırsa exception olarak yükseliyor mu?"""
        # jwt.encode hata fırlatacak şekilde ayarla
        mock_encode.side_effect = Exception("encode fail")
        # generate_jwt'in bu hatayı propagate etmesi beklenir
        with self.assertRaises(Exception) as cm:
            generate_jwt("a@b.com", "user")
        self.assertEqual(str(cm.exception), "encode fail")

    def test_validate_jwt_valid_token(self):
        """Geçerli token başarıyla doğrulanıyor mu?"""
        token = generate_jwt("a@b.com", "user")
        result = validate_jwt(token)
        # Hata içermemeli, payload döndürülmeli
        self.assertNotIn("error", result)
        self.assertEqual(result["email"], "a@b.com")
        self.assertEqual(result["role"], "user")

    def test_validate_jwt_invalid_format(self):
        """Bozuk/tamper edilmiş token 'Geçersiz Token' hatası veriyor mu?"""
        bad = "bozuk.token.degistir"
        result = validate_jwt(bad)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Geçersiz Token")

    def test_validate_jwt_empty_or_none(self):
        """Empty string veya None token 'Geçersiz Token' hatası veriyor mu?"""
        for bad in ("", None):
            result = validate_jwt(bad)
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Geçersiz Token")

    def test_validate_jwt_expired_token(self):
        """Süresi dolmuş token 'Token süresi doldu' hatası veriyor mu?"""
        # 1 saniyelik expiration ver, 2s bekle, sonra doğrula
        token = generate_jwt("a@b.com", "user", expiration=1)
        time.sleep(2)
        result = validate_jwt(token)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Token süresi doldu")

    def test_validate_jwt_tampered_signature(self):
        """İmzası bozulan token 'Geçersiz Token' hatası veriyor mu?"""
        token = generate_jwt("a@b.com", "user")
        # Son karakteri değiştirerek imzayı boz
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        result = validate_jwt(tampered)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Geçersiz Token")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAuth)
    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    runner.run(suite)

# cd "C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project"
# pytest testler/test_auth.py