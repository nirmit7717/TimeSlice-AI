"""Auth API Router — Local JWT authentication.

Endpoints:
  POST /api/v1/auth/register   → Create account
  POST /api/v1/auth/login      → Authenticate and get JWT
  POST /api/v1/auth/refresh    → Refresh a valid token
  POST /api/v1/auth/logout     → Invalidate session (client-side)
  GET  /api/v1/auth/me         → Get current user from token

Architecture note:
  Uses local JWT + bcrypt. To migrate to AWS Cognito, replace the
  login handler with a Cognito InitiateAuth API call and replace
  decode_token with Cognito JWT JWKS verification.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth import create_access_token, verify_password, hash_password, decode_token
from app.dependencies import get_db
from database.models import DbUser

router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Request / Response schemas ─────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = "Developer"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_email: str
    user_name: str


class UserResponse(BaseModel):
    email: str
    name: str
    created_at: datetime


# ── Dependency: resolve current user from Bearer token ─────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> DbUser:
    """
    FastAPI dependency that extracts the authenticated user from the
    Bearer JWT in the Authorization header.
    """
    payload = decode_token(token)
    email: str = payload.get("sub")
    user = db.query(DbUser).filter(DbUser.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """
    Creates a new local user account and returns a JWT.
    Email must be unique.
    """
    existing = db.query(DbUser).filter(DbUser.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email '{body.email}' already exists.",
        )
    user = DbUser(
        id=str(uuid.uuid4()),
        email=body.email,
        hashed_password=hash_password(body.password),
        name=body.name,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email, "name": user.name})
    return LoginResponse(
        access_token=token,
        user_email=user.email,
        user_name=user.name,
    )


@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates with email + password and returns a signed JWT.
    OAuth2PasswordRequestForm uses 'username' field for email.
    """
    user = db.query(DbUser).filter(DbUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token({"sub": user.email, "name": user.name})
    return LoginResponse(
        access_token=token,
        user_email=user.email,
        user_name=user.name,
    )


@router.post("/refresh", response_model=LoginResponse)
def refresh_token(
    current_user: DbUser = Depends(get_current_user),
):
    """
    Returns a fresh token for an already-authenticated user.
    The old token must still be valid to call this endpoint.
    """
    token = create_access_token({"sub": current_user.email, "name": current_user.name})
    return LoginResponse(
        access_token=token,
        user_email=current_user.email,
        user_name=current_user.name,
    )


@router.post("/logout")
def logout():
    """
    Stateless logout — instructs the client to discard the token.
    For Phase 7, this will add the token to a Redis deny-list.
    """
    return {"message": "Logged out successfully. Discard your local token."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: DbUser = Depends(get_current_user)):
    """Returns the currently authenticated user's profile."""
    return UserResponse(
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
    )
