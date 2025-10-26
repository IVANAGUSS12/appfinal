from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from .config import settings

pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def now_str(): 
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def hash_password(pw: str) -> str: 
    return pwd_ctx.hash(pw)

def verify_password(pw: str, hashed: str) -> bool: 
    return pwd_ctx.verify(pw, hashed)

def create_token(data: dict) -> str:
    payload = data.copy()
    payload.update({"exp": datetime.utcnow() + timedelta(minutes=settings.jwt_exp_minutes)})
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")
