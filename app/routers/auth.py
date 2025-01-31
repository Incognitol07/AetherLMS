# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    verify_password,
    hash_password,
)
from app.utils.helpers.auth import get_by_email, create_user
from app.schemas.auth import Token, RefreshTokenRequest, UserCreate
from app.models.user import UserRole

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # Fetch user from the database
    user = await get_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role.value})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    # Verify the refresh token
    payload = verify_refresh_token(refresh_token_request.refresh_token)
    user_email = payload.get("sub")
    user_role = payload.get("role")

    # Fetch user from the database
    user = await get_by_email(db, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Create a new access token
    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/signup")
async def signup(
    email: str,
    password: str,
    role: UserRole,
    db: AsyncSession = Depends(get_db),
):
    # Check if user already exists
    existing_user = await get_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Hash the password
    hashed_password = hash_password(password)

    # Create a new user
    user_data = UserCreate(email=email, password=password, role=role, hashed_password=hashed_password)
    new_user = await create_user(db, user_data)

    return {"message": "User created successfully", "user_id": new_user.id}