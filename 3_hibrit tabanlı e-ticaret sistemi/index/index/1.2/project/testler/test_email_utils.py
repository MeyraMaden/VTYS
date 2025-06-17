# testler/test_email_utils.py

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from email import message_from_string
from email.header import decode_header, make_header

# Proje kökünü path’e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from back.util.email_utils import send_email, send_email_to_users

@pytest.fixture
def mock_smtp():
    """smtplib.SMTP’yi patch’ler"""
    with patch("smtplib.SMTP") as m:
        yield m

# ---------- send_email (şifre sıfırlama) ----------

def test_send_email_success(mock_smtp):
    """✅ send_email: tüm adımlar ve içerik doğru mu?"""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    to_addr = "test@example.com"
    token   = "ABC123"
    send_email(to_addr, token)

    # 1) SMTP(...) constructor
    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)

    # 2) starttls & login
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with(
        "helinnbaglamis@gmail.com",
        "ojdkiyhkruwcbunk"
    )

    # 3) sendmail argümanlarını incele
    sender, recipient, raw_msg = mock_server.sendmail.call_args[0]
    assert sender    == "helinnbaglamis@gmail.com"
    assert recipient == to_addr

    # raw_msg’dan MIME mesajını parse et
    msg = message_from_string(raw_msg)
    # Subject başlığını decode et
    decoded_subject = str(make_header(decode_header(msg["Subject"])))
    assert decoded_subject == "Şifre Sıfırlama İsteği"

    # Body’yi Base64’ten decode edip gerçek metni al
    body = msg.get_payload(decode=True).decode('utf-8')
    assert f"?token={token}" in body

    # 4) quit çağrıldı mı?
    mock_server.quit.assert_called_once()

@pytest.mark.parametrize("stage,exc_msg", [
    ("starttls", "TLS fail"),
    ("login",    "Login fail"),
    ("sendmail", "Send fail"),
    ("quit",     "Quit fail"),
])
def test_send_email_exceptions(mock_smtp, stage, exc_msg):
    """⚠ send_email: her SMTP aşamasında hata fırlat ve mesajı propagate et"""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    getattr(mock_server, stage).side_effect = Exception(exc_msg)

    with pytest.raises(Exception) as e:
        send_email("a@b.com", "TOK")
    assert exc_msg in str(e.value)

def test_send_email_smtp_constructor_failure():
    """⚠ send_email: SMTP constructor aşamasındaki hata ele alınmalı"""
    with patch("smtplib.SMTP", side_effect=Exception("Cannot open SMTP")):
        with pytest.raises(Exception) as e:
            send_email("a@b.com", "TOK")
    assert "Cannot open SMTP" in str(e.value)

@pytest.mark.parametrize("to_email,token", [
    ("",       "ABC"),      # boş e-posta
    (None,     "ABC"),      # None e-posta
    ("a@b.com",""),         # boş token
    ("a@b.com", None),      # None token
])
def test_send_email_invalid_params(mock_smtp, to_email, token):
    """⚠ send_email: invalid parametreler ValueError fırlatmalı"""
    with pytest.raises(ValueError):
        send_email(to_email, token)


# ---------- send_email_to_users (stok bildirimi) ----------

def test_send_email_to_users_success(mock_smtp):
    """✅ send_email_to_users: tüm adımlar ve içerik doğru mu?"""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    user_addr    = "user@example.com"
    product_name = "Laptop Pro"
    send_email_to_users(user_addr, product_name)

    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with(
        "helinnbaglamis@gmail.com",
        "ojdkiyhkruwcbunk"
    )

    sender, recipient, raw_msg = mock_server.sendmail.call_args[0]
    assert sender    == "helinnbaglamis@gmail.com"
    assert recipient == user_addr

    msg = message_from_string(raw_msg)
    decoded_subject = str(make_header(decode_header(msg["Subject"])))
    assert decoded_subject == "Sepetinizdeki Ürün Güncellendi"

    body = msg.get_payload(decode=True).decode('utf-8')
    assert product_name in body
    assert "stokta bulunmamaktadır" in body

    mock_server.quit.assert_called_once()

@pytest.mark.parametrize("stage,exc_msg", [
    ("starttls", "TLS fail"),
    ("login",    "Login fail"),
    ("sendmail", "Send fail"),
    ("quit",     "Quit fail"),
])
def test_send_email_to_users_exceptions(mock_smtp, stage, exc_msg):
    """⚠ send_email_to_users: her SMTP aşamasında hata fırlat ve propagate et"""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    getattr(mock_server, stage).side_effect = Exception(exc_msg)

    with pytest.raises(Exception) as e:
        send_email_to_users("u@v.com", "ITEM")
    assert exc_msg in str(e.value)

def test_send_email_to_users_smtp_constructor_failure():
    """⚠ send_email_to_users: SMTP constructor hatası yakalanmalı"""
    with patch("smtplib.SMTP", side_effect=Exception("SMTP down")):
        with pytest.raises(Exception) as e:
            send_email_to_users("u@v.com", "ITEM")
    assert "SMTP down" in str(e.value)

@pytest.mark.parametrize("user_email,product_name", [
    ("",       "Prod"),     # boş e-posta
    (None,     "Prod"),     # None e-posta
    ("u@v.com",""),         # boş ürün adı
    ("u@v.com",None),       # None ürün adı
])
def test_send_email_to_users_invalid_params(mock_smtp, user_email, product_name):
    """⚠ send_email_to_users: invalid parametreler ValueError fırlatmalı"""
    with pytest.raises(ValueError):
        send_email_to_users(user_email, product_name)



#  cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
#   pytest testler/test_email_utils.py