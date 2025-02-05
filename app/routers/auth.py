# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserRole, Role
from app.database import get_db
from app.utils import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    verify_password,
    get_user_by_email,
    get_admin_by_id,
    create_user,
    logger,
    create_student,
    create_instructor,
)
from app.schemas.auth import Token, RefreshTokenRequest, UserCreate, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])

ADMIN_ROLE_SCOPES = {
    "superadmin": ["admin", "admin:super"],
    "moderator": ["admin", "admin:moderate"],
    "content_manager": ["admin", "admin:content"],
    "support": ["admin", "admin:support"],
}

VALID_ADMIN_ROLES = {"superadmin", "moderator", "content_manager", "support"}


# app/routers/auth.py
@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Determine scopes based on user role and permissions
    scopes = []
    if user.role == UserRole.STUDENT:
        scopes = ["student"]
    elif user.role == UserRole.INSTRUCTOR:
        scopes = ["instructor"]
    elif user.role == UserRole.ADMIN:
        admin = await get_admin_by_id(db, user.id)
        if not admin or not admin.role:
            logger.error(f"Admin role missing for user {user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator account not properly configured",
            )
        if admin.role.name not in VALID_ADMIN_ROLES:
            logger.error(f"Invalid admin role: {admin.role.name}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid role configuration",
            )
        scopes = ADMIN_ROLE_SCOPES.get(admin.role.name, ["admin"])

    access_token = create_access_token(data={"sub": user.email, "scopes": scopes})
    refresh_token = create_refresh_token(data={"sub": user.email, "scopes": scopes})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "scopes": scopes,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = verify_refresh_token(refresh_token_request.refresh_token)
    user_email = payload.get("sub")

    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Determine scopes based on user role and permissions
    scopes = []
    if user.role == UserRole.STUDENT:
        scopes = ["student"]
    elif user.role == UserRole.INSTRUCTOR:
        scopes = ["instructor"]
    elif user.role == UserRole.ADMIN:
        admin = await get_admin_by_id(db, user.id)
        if admin.role.name not in VALID_ADMIN_ROLES:
            logger.error(f"Invalid admin role: {admin.role.name}")
            raise HTTPException(status_code=500, detail="Invalid role configuration")
        scopes = ADMIN_ROLE_SCOPES.get(admin.role.name, ["admin"])

    access_token = create_access_token(data={"sub": user.email, "scopes": scopes})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signup")
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    # Prevent users from signing up as an admin
    if user_data.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Signing up as an admin is not allowed.",
        )

    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    new_user = await create_user(db, user_data)
    if new_user.role == UserRole.STUDENT:
        new_student = await create_student(db, new_user.id)
    if new_user.role == UserRole.INSTRUCTOR:
        new_instructor = await create_instructor(db, new_user.id)

    return {"message": "User created successfully", "user_id": new_user.id}
