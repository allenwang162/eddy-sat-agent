import base64
import hashlib
import hmac
import json
import os
from typing import Any

from backend.config import env


def base64_url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def random_url_token(length: int = 32) -> str:
    return base64_url(os.urandom(length))


def sha256_base64_url(value: str) -> str:
    return base64_url(hashlib.sha256(value.encode("utf-8")).digest())


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def hash_password(password: str, salt: str | None = None) -> dict[str, str]:
    salt = salt or random_url_token(24)
    digest = hashlib.pbkdf2_hmac("sha256", str(password).encode("utf-8"), salt.encode("utf-8"), 210000, dklen=32)
    return {"salt": salt, "hash": base64.b64encode(digest).decode("ascii")}


def verify_password(password: str, password_record: dict[str, str] | None) -> bool:
    if not password_record or "salt" not in password_record or "hash" not in password_record:
        return False
    candidate = hash_password(password, password_record["salt"])["hash"]
    return hmac.compare_digest(candidate, password_record["hash"])


def _encryption_key() -> bytes:
    return hashlib.sha256(env.AUTH_SECRET.encode("utf-8")).digest()


def encrypt_json(value: Any) -> dict[str, str]:
    nonce = os.urandom(16)
    plaintext = json.dumps(value).encode("utf-8")
    key = _encryption_key()
    stream = b"".join(
        hmac.new(key, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest()
        for counter in range((len(plaintext) // 32) + 1)
    )
    ciphertext = bytes(left ^ right for left, right in zip(plaintext, stream))
    tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    return {
        "alg": "hmac-sha256-stream",
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "tag": base64.b64encode(tag).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
    }


def decrypt_json(record: dict[str, str] | None):
    if not record or "nonce" not in record or "tag" not in record or "ciphertext" not in record:
        return None
    key = _encryption_key()
    nonce = base64.b64decode(record["nonce"])
    ciphertext = base64.b64decode(record["ciphertext"])
    expected_tag = hmac.new(key, nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_tag, base64.b64decode(record["tag"])):
        raise ValueError("Encrypted token payload failed authentication")
    stream = b"".join(
        hmac.new(key, nonce + counter.to_bytes(4, "big"), hashlib.sha256).digest()
        for counter in range((len(ciphertext) // 32) + 1)
    )
    plaintext = bytes(left ^ right for left, right in zip(ciphertext, stream))
    return json.loads(plaintext.decode("utf-8"))
