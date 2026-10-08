"""Password hashing and login sessions for Campus Customs.

Password format (matches the seeded users in data/campus_customs.db):
    pbkdf2_sha256$<salt>$<hex digest>
    digest = PBKDF2-HMAC-SHA256(password, salt, 120_000 iterations), hex-encoded (32 bytes)

Sessions: after signup/login the browser gets an HttpOnly cookie holding
"<user_id>.<expiry>.<HMAC signature>". The signature uses SESSION_SECRET, so the
cookie can't be forged or edited, and JavaScript can't read it.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000  # same as the seeded accounts
SESSION_COOKIE = "cc_session"
SESSION_MAX_AGE = 7 * 24 * 3600  # stay logged in for 7 days

_SECRET_FILE = Path(__file__).resolve().parent / ".session_secret"


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)  # 16 hex characters, like the seeded users
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS).hex()
    return f"{ALGORITHM}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, salt, digest = stored.split("$")
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS).hex()
    return hmac.compare_digest(candidate, digest)  # constant-time comparison


def _secret() -> bytes:
    """SESSION_SECRET from the environment, or a random one saved locally (never committed)."""
    env = os.getenv("SESSION_SECRET", "").strip()
    if env:
        return env.encode()
    if not _SECRET_FILE.exists():
        _SECRET_FILE.write_text(secrets.token_hex(32))
        _SECRET_FILE.chmod(0o600)
    return _SECRET_FILE.read_text().strip().encode()


def _sign(payload: str) -> str:
    return hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()


def make_session_token(user_id: int) -> str:
    payload = f"{user_id}.{int(time.time()) + SESSION_MAX_AGE}"
    return f"{payload}.{_sign(payload)}"


def read_session_token(token: str | None) -> int | None:
    """The user ID in a valid, unexpired token, otherwise None."""
    if not token:
        return None
    try:
        user_id, expires, signature = token.split(".")
    except ValueError:
        return None
    if not hmac.compare_digest(_sign(f"{user_id}.{expires}"), signature):
        return None
    if not expires.isdigit() or int(expires) < time.time():
        return None
    return int(user_id) if user_id.isdigit() else None
