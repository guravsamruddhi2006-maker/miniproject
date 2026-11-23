"""
Security, password hashing, and JWT token management.
Implements robust PBKDF2-SHA256 hashing and HMAC-SHA256 JWT tokens with zero external dependency failures.
"""
import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from app.core.config import ALGORITHM, SECRET_KEY


def hash_password(password: str) -> str:
    """
    Hashes a password with a random salt using PBKDF2-HMAC-SHA256.
    Returns format: salt$hash
    """
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the stored salt$hash string.
    """
    try:
        salt, expected_hash = hashed_password.split("$", 1)
        key = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return hmac.compare_digest(key.hex(), expected_hash)
    except Exception:
        return False


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(s: str) -> bytes:
    padding = 4 - (len(s) % 4)
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s.encode("utf-8"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates an RFC 7519 compliant JWT token (HS256) with expiration.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": int(expire.timestamp())})

    header = {"alg": ALGORITHM, "typ": "JWT"}
    header_b64 = _base64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(to_encode).encode("utf-8"))

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifies signature and expiration of JWT, returning the payload if valid.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(
            SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        actual_sig = _base64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        # Decode payload
        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Check expiration
        exp = payload.get("exp")
        if exp and int(time.time()) > exp:
            return None

        return payload
    except Exception:
        return None
