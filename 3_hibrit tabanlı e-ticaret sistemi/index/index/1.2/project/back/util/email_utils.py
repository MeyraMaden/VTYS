# back/utils/email_utils.py
import smtplib
from email.mime.text import MIMEText

def send_email(to_email, token):
    # Parametre validasyonu
    if not to_email or not isinstance(to_email, str):
        raise ValueError("Invalid to_email parameter")
    if not token or not isinstance(token, str):
        raise ValueError("Invalid token parameter")

    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "helinnbaglamis@gmail.com"
        sender_password = "ojdkiyhkruwcbunk"

        subject = "Şifre Sıfırlama İsteği"
        body = (
            "Lütfen şifrenizi sıfırlamak için aşağıdaki bağlantıyı kullanın:\n\n"
            f"http://127.0.0.1:5000/reset-password?token={token}"
        )

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

    except Exception as e:
        print(f"E-posta gönderim hatası: {e}")
        raise e


def send_email_to_users(user_email, product_name):
    # Parametre validasyonu
    if not user_email or not isinstance(user_email, str):
        raise ValueError("Invalid user_email parameter")
    if not product_name or not isinstance(product_name, str):
        raise ValueError("Invalid product_name parameter")

    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "helinnbaglamis@gmail.com"
        sender_password = "ojdkiyhkruwcbunk"

        subject = "Sepetinizdeki Ürün Güncellendi"
        body = (
            f"Merhaba,\n\n"
            f"'{product_name}' adlı ürün artık stokta bulunmamaktadır ve sepetinizden kaldırılmıştır. "
            "Yeni ürünlerimize göz atmayı unutmayın!"
        )

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = user_email

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()

        print("Kullanıcıya bilgilendirme e-postası gönderildi!")

    except Exception as e:
        print(f"E-posta gönderim hatası: {e}")
        raise e

