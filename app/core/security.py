from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import get_settings

# bcrypt 对密码长度限制为 72 字节，超出部分会被截断
BCRYPT_MAX_BYTES = 72


def _normalize_password(password: str) -> bytes:
    data = password.encode("utf-8")
    if len(data) > BCRYPT_MAX_BYTES:
        data = data[:BCRYPT_MAX_BYTES]
    return data


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_normalize_password(password), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            _normalize_password(password),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes,
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
