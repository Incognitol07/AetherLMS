# app/utils/dependencies/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, Admin, UserRole
from pydantic import BaseModel
from app.utils import (
    verify_access_token, 
    get_by_email, 
    logger
    )
# app/utils/dependencies/auth.py
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

# Define scopes and their descriptions
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)

# Update TokenData schema
class TokenData(BaseModel):
    email: str | None = None
    scopes: list[str] = []

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = verify_access_token(token)
        if payload is None:
            raise credentials_exception

        email: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        
        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email, scopes=token_scopes)
    # Replace generic Exception with specific errors
    except jwt.PyJWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise credentials_exception
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

    user = await get_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception

    # Verify scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user

# app/utils/dependencies/auth.py
from fastapi import Security

# Basic role-based scopes
def require_scope(scope: str):
    async def _require_scope(
        current_user: User = Security(get_current_user, scopes=[scope])
    ):
        return current_user
    return _require_scope

def require_admin_subscope(scope: str):
    async def _require_admin_subscope(
        current_user: User = Security(get_current_user, scopes=["admin", scope])
    ):
        return current_user
    return _require_admin_subscope


# Specific scope dependencies
get_current_student = require_scope("student")
get_current_instructor = require_scope("instructor")
get_current_admin = require_scope("admin")
get_superadmin = require_admin_subscope("admin:super")
get_moderator = require_admin_subscope("admin:moderate")
get_content_manager = require_admin_subscope("admin:content")
get_support_admin = require_admin_subscope("admin:support")
