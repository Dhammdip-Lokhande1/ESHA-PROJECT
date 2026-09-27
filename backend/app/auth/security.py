"""
auth/security.py — Cryptographic password hashing and JWT token handling.

Zero paid APIs, zero external native libraries — relies on Python stdlib:
  - Password hashing: PBKDF2-HMAC-SHA256 with 100,000 iterations + 16-byte random salt.
  - JWT Tokens: HS256 HMAC-SHA256 signature with Base64URL encoding.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app.config import settings

# Secret key for signing JWTs (defaults to config settings)
JWT_SECRET_KEY = getattr(settings, "SECRET_KEY", "ehsa-secret-key-change-in-production-2026")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


# ──────────────────────────────────────────────────────────────────────────────
# Password Hashing & Verification
# ──────────────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using PBKDF2-HMAC-SHA256.
    Returns format: 'pbkdf2_sha256$600000$salt_hex$hash_hex'
    """
    salt = secrets.token_bytes(16)
    iterations = getattr(settings, "PBKDF2_ITERATIONS", 600_000)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${derived.hex()}"


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify a plaintext password against a stored PBKDF2 hash.
    Safe against timing attacks via hmac.compare_digest. Supports legacy iteration counts.
    """
    try:
        parts = password_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
        computed_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(computed_hash, expected_hash)
    except Exception:
        return False


def needs_rehash(password_hash: str) -> bool:
    """
    Check if stored password hash uses fewer iterations than current configured target.
    """
    try:
        parts = password_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return True
        iterations = int(parts[1])
        target_iterations = getattr(settings, "PBKDF2_ITERATIONS", 600_000)
        return iterations < target_iterations
    except Exception:
        return True


# ──────────────────────────────────────────────────────────────────────────────
# JWT Token Generation & Verification
# ──────────────────────────────────────────────────────────────────────────────

def _b64url_encode(data: bytes) -> str:
    """Base64URL encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    """Base64URL decode with padding restoration."""
    padding = "=" * (4 - (len(data) % 4)) if len(data) % 4 != 0 else ""
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an HS256-signed JWT access token.
    Payload typically contains: sub (user_id), username, role.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=TOKEN_EXPIRE_HOURS)

    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp())
    })

    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    
    header_json = json.dumps(header, separators=(",", ":")).encode("utf-8")
    payload_json = json.dumps(to_encode, separators=(",", ":")).encode("utf-8")

    header_b64 = _b64url_encode(header_json)
    payload_b64 = _b64url_encode(payload_json)

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and verify an HS256 JWT access token.
    Returns payload dict if valid, or None if expired/tampered/malformed.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify expiration
        exp = payload.get("exp")
        if exp is not None:
            now = datetime.now(timezone.utc).timestamp()
            if now > exp:
                return None

        return payload
    except Exception:
        return None
