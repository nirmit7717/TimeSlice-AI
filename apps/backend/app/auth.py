"""Local JWT authentication utilities.

Provides token creation and verification using python-jose.
Secret key is read from JWT_SECRET_KEY env var (defaults to a dev key).

To swap for AWS Cognito later, replace `decode_token` with a Cognito
JWT verifier using the User Pool's JWKS endpoint.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status

# ── Configuration ──────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "timeslice-dev-secret-change-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24h default


# ── Password utilities ─────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Returns a bcrypt-hashed password string using direct bcrypt."""
    pw_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Returns True if the plaintext matches the stored hash using direct bcrypt."""
    pw_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False


# ── Token utilities ────────────────────────────────────────────────────────────

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Creates a signed JWT access token.

    Args:
        data: Payload dict (must include 'sub' = user email).
        expires_delta: Optional custom expiry; defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.

    Returns:
        Payload dict.

    Raises:
        HTTPException 401 if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception
