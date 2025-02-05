# app/routers/admin.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Role, Admin, User
from app.utils import (
    get_current_admin,
    get_superadmin,
    logger,
    get_user_by_email,
    create_user,
    get_role_by_name,
    get_admin_by_id,
    get_role_by_id,
    get_user_by_id
)
from app.schemas.admin import AdminResponse, AdminCreate, AdminUpdate

router = APIRouter(prefix="/admin", tags=["admin"])

# ------------------------------ Role Management Endpoints ------------------------------


@router.get("/roles")
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),  # Any admin can list roles
):
    """
    List all roles.
    """
    try:
        roles = await db.execute(select(Role))
        return roles.scalars().all()
    except Exception as e:
        logger.error(f"Error listing roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/roles/{role_id}")
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),  # Any admin can view roles
):
    """
    Get details of a specific role.
    """
    try:
        role = await db.execute(select(Role).filter(Role.id == role_id))
        role = role.scalars().first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        return role
    except Exception as e:
        logger.error(f"Error fetching role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# ------------------------------ Admin User Management Endpoints ------------------------------


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin_data: AdminCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_superadmin),  # Superadmin can create admins
):
    """
    Create a new admin.
    """
    try:
        existing_user = await get_user_by_email(db, admin_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        new_user = await create_user(db, admin_data, is_admin=True)

        role = await get_role_by_name(db, name=admin_data.admin_sub_role)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role does not exist",
            )

        # Create the admin
        admin = Admin(id=new_user.id, role_id=role.id)
        db.add(admin)
        await db.commit()
        logger.info(
            f"Admin created for user ID '{admin.id}' by admin '{current_admin.email}'."
        )
        return {"message": "Admin created successfully", "admin_id": admin.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=list[AdminResponse])
async def list_admins(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),  # Any admin can list admins
):
    """
    List all admins.
    """
    try:
        admins = await db.execute(
            select(Admin).options(selectinload(Admin.role), selectinload(Admin.user))
        )
        result = admins.scalars().all()
        return [
            {
                "created_at": admin.created_at,
                "updated_at": admin.updated_at,
                "role_id": admin.role_id,
                "role_name": admin.role.name,
                "id": admin.id,
                "full_name": admin.user.full_name,
            }
            for admin in result
        ]
    except Exception as e:
        logger.error(f"Error listing admins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/sub-role")
async def get_admin_sub_role(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    admin = await get_admin_by_id(db, current_admin.id)

    if not admin or not admin.role_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin sub-role not found",
        )

    return {"admin_sub_role": admin.role.name}


@router.get("/{admin_id}", response_model=AdminResponse)
async def get_admin(
    admin_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),  # Any admin can view admins
):
    """
    Get details of a specific admin.
    """
    try:
        admin = await get_admin_by_id(db, admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found"
            )
        return {
            "created_at": admin.created_at,
            "updated_at": admin.updated_at,
            "role_id": admin.role_id,
            "role_name": admin.role.name,
            "id": admin.id,
            "full_name": admin.user.full_name,
        }
    except Exception as e:
        logger.error(f"Error fetching admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{admin_id}")
async def update_admin(
    admin_id: UUID,
    admin_data: AdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_superadmin),  # Superadmin can update admins
):
    """
    Update an admin.
    """
    try:
        admin = await get_admin_by_id(db, admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found"
            )

        # Update admin fields
        if admin_data.role_id:
            admin.role_id = admin_data.role_id

        await db.commit()
        logger.info(f"Admin '{admin.id}' updated by admin '{current_admin.email}'.")
        return {"message": f"Admin '{admin.user.full_name}' updated successfully"}
    except Exception as e:
        logger.error(f"Error updating admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(
    admin_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_superadmin),  # Superadmin can delete admins
):
    """
    Delete an admin.
    """
    try:
        admin = await get_admin_by_id(db, admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found"
            )
        
        user = await get_user_by_id(db, admin.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await db.delete(admin)
        await db.delete(user)
        await db.commit()
        logger.info(f"Admin '{admin.id}' deleted by admin '{current_admin.email}'.")
    except Exception as e:
        logger.error(f"Error deleting admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
