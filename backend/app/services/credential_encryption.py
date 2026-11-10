import os
import json

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv("INTEGRATION_ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise RuntimeError("Integration encryption key is not configured.")

try:
    cipher = Fernet(ENCRYPTION_KEY.encode())
except Exception:
    raise RuntimeError("Invalid integration encryption key.")


def encrypt_credentials(credentials: dict) -> str:
    try:
        payload = json.dumps(credentials).encode("utf-8")
        return cipher.encrypt(payload).decode("utf-8")
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to encrypt integration credentials."
        )


def decrypt_credentials(encrypted_credentials: str) -> dict:
    try:
        decrypted = cipher.decrypt(
            encrypted_credentials.encode("utf-8")
        )
        return json.loads(decrypted.decode("utf-8"))
    except (InvalidToken, ValueError):
        raise HTTPException(
            status_code=500,
            detail="Unable to decrypt integration credentials."
        )