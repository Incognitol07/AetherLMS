# app/routers/auth.py

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status, 
    Response, 
    Request
    )
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Role
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
    REFRESH_TOKEN_EXPIRE_DAYS,
    get_role_by_name
)
from app.schemas.auth import Token, UserCreate, LoginResponse
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

ADMIN_ROLE_SCOPES = {
    "superadmin": ["admin", "admin:super"],
    "moderator": ["admin", "admin:moderate"],
    "content_manager": ["admin", "admin:content"],
    "support": ["admin", "admin:support"],
}

# app/routers/auth.py
@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
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
    if user.role.name == "student":
        scopes = ["student"]
    elif user.role.name == "instructor":
        scopes = ["instructor"]
    else:
        admin = await get_admin_by_id(db, user.id)
        if not admin or not admin.user.role:
            logger.error(f"Admin role missing for user {user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator account not properly configured",
            )
        if admin.user.role.name not in  ADMIN_ROLE_SCOPES.keys():
            logger.error(f"Invalid admin role: {admin.role.name}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid role configuration",
            )
        scopes = ADMIN_ROLE_SCOPES.get(admin.user.role.name, ["admin"])

    access_token = create_access_token(data={"sub": user.email, "scopes": scopes})
    refresh_token = create_refresh_token(data={"sub": user.email, "scopes": scopes})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Prevent JavaScript access (XSS protection)
        secure=False if settings.DEBUG else True,    # Use HTTPS only (production best practice)
        samesite="Strict",  # Prevent CSRF (adjust as needed)
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Expiry in seconds
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "scopes": scopes,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )
    
    payload = verify_refresh_token(refresh_token)
    user_email = payload.get("sub")

    user = await get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Determine scopes based on user role and permissions
    scopes = []
    if user.role.name == "student":
        scopes = ["student"]
    elif user.role.name == "instructor":
        scopes = ["instructor"]
    else:
        if user.role.name not in ADMIN_ROLE_SCOPES.keys():
            logger.error(f"Invalid admin role: {user.role.name}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Invalid role configuration"
                )
        admin = await get_admin_by_id(db, user.id)
        scopes = ADMIN_ROLE_SCOPES.get(user.role.name, ["admin"])

    access_token = create_access_token(data={"sub": user.email, "scopes": scopes})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signup")
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Check if user already exists
        existing_user = await get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        if user_data.role_name not in {"student", "instructor"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )
        new_user = await create_user(db, user_data, role_name=user_data.role_name)
        if user_data.role_name == "student":
            await create_student(db, new_user.id)
        if user_data.role_name == "instructor":
            await create_instructor(db, new_user.id)

        return {"message": f"{user_data.role_name.title()} created successfully", "user_id": new_user.id}
    except Exception as e:
        logger.error(f"Unexpected error during signup: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
