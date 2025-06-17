# auth.py
import jwt
import datetime
from back.config import SECRET_KEY
def generate_jwt(email, role, expiration=7 * 24 * 60 * 60):  # ✅ Varsayılan olarak 7 gün
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expiration),
        "iat": datetime.datetime.utcnow()  # ✅ Oluşturulma zamanı eklendi!
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def validate_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"error": "Token süresi doldu"}
    except jwt.InvalidTokenError:
        return {"error": "Geçersiz Token"}
