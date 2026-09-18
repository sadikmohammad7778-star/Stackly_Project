from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from jose import jwt, JWTError

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
)


def create_access_token(data: dict):
    payload = data.copy()

    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({
        "type": "access",
        "iat": now,
        "exp": expire,
    })

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_refresh_token(data: dict):
    payload = data.copy()

    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload.update({
        "type": "refresh",
        "iat": now,
        "exp": expire,
    })

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str):
    """
    Decode and verify a JWT token.
    Returns the payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload
    except JWTError:
        return None