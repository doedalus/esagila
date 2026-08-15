from datetime import datetime, timedelta
from pwdlib import PasswordHash
from jose import jwt, JWTError
from app.settings import settings

ALGORITHM = "HS256"
SECRET_KEY = settings.secret_key

password_hash = PasswordHash.recommended()

def hash_password(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.now() + timedelta(minutes=30)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None