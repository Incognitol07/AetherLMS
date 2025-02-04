# app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Role, Admin, User
from app.utils import (
    get_current_admin,
    get_superadmin,
    logger,
    get_moderator,
    get_support_admin,
    get_content_manager,
    get_by_email,
    create_user,
    get_role_by_name
)
from app.schemas.admin import RoleCreate, RoleUpdate, PermissionUpdate, AdminCreate, AdminUpdate

router = APIRouter(prefix="/admin", tags=["admin"])

# ------------------------------ Role Management Endpoints ------------------------------

# @router.post("/roles", status_code=status.HTTP_201_CREATED)
# async def create_role(
#     role_data: RoleCreate,
#     db: AsyncSession = Depends(get_db),
#     current_admin: Admin = Depends(get_superadmin)  # Only superadmin can create roles
# ):
#     """
#     Create a new role.
#     """
#     try:
#         # Check if role already exists
#         existing_role = await db.execute(select(Role).filter(Role.name == role_data.name))
#         if existing_role.scalars().first():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Role with this name already exists"
#             )

#         # Create the role
#         role = Role(name=role_data.name, permissions=role_data.permissions)
#         db.add(role)
#         await db.commit()
#         logger.info(f"Role '{role.name}' created by admin '{current_admin.email}'.")
#         return {"message": "Role created successfully", "role_id": role.id}
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error creating role: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error"
#         )


@router.get("/roles")
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Any admin can list roles
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
            detail="Internal server error"
        )


@router.get("/roles/{role_id}")
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Any admin can view roles
):
    """
    Get details of a specific role.
    """
    try:
        role = await db.execute(select(Role).filter(Role.id == role_id))
        role = role.scalars().first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role
    except Exception as e:
        logger.error(f"Error fetching role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# @router.put("/roles/{role_id}")
# async def update_role(
#     role_id: str,
#     role_data: RoleUpdate,
#     db: AsyncSession = Depends(get_db),
#     current_admin: Admin = Depends(get_superadmin)  # Superadmin can update roles
# ):
#     """
#     Update a role.
#     """
#     try:
#         role = await db.execute(select(Role).filter(Role.id == role_id))
#         role = role.scalars().first()
#         if not role:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Role not found"
#             )

#         # Update role fields
#         if role_data.name:
#             role.name = role_data.name
#         if role_data.permissions:
#             role.permissions = role_data.permissions

#         await db.commit()
#         logger.info(f"Role '{role.name}' updated by admin '{current_admin.email}'.")
#         return {"message": "Role updated successfully"}
#     except Exception as e:
#         logger.error(f"Error updating role: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error"
#         )


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_superadmin)  # Any admin can delete roles
):
    """
    Delete a role.
    """
    try:
        role = await db.execute(select(Role).filter(Role.id == role_id))
        role = role.scalars().first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        await db.delete(role)
        await db.commit()
        logger.info(f"Role '{role.name}' deleted by admin '{current_admin.email}'.")
    except Exception as e:
        logger.error(f"Error deleting role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/roles/{role_id}/permissions")
async def add_permission_to_role(
    role_id: str,
    permission_data: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Any admin can add permissions
):
    """
    Add a permission to a role.
    """
    try:
        role = await db.execute(select(Role).filter(Role.id == role_id))
        role = role.scalars().first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        # Add the permission if it doesn't already exist
        if permission_data.permission not in role.permissions:
            role.add_permission(permission_data.permission)
            await db.commit()
            logger.info(f"Permission '{permission_data.permission}' added to role '{role.name}' by admin '{current_admin.email}'.")
            return {"message": "Permission added successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists"
            )
    except Exception as e:
        logger.error(f"Error adding permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/roles/{role_id}/permissions")
async def remove_permission_from_role(
    role_id: str,
    permission_data: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_superadmin)  # Any admin can remove permissions
):
    """
    Remove a permission from a role.
    """
    try:
        role = await db.execute(select(Role).filter(Role.id == role_id))
        role = role.scalars().first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        # Remove the permission if it exists
        if permission_data.permission in role.permissions:
            role.remove_permission(permission_data.permission)
            await db.commit()
            logger.info(f"Permission '{permission_data.permission}' removed from role '{role.name}' by admin '{current_admin.email}'.")
            return {"message": "Permission removed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission does not exist"
            )
    except Exception as e:
        logger.error(f"Error removing permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ------------------------------ Admin User Management Endpoints ------------------------------

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin_data: AdminCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_superadmin)  # Superadmin can create admins
):
    """
    Create a new admin.
    """
    try:
        existing_user = await get_by_email(db, admin_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        
        new_user = await create_user(db, admin_data,is_admin=True)

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
        logger.info(f"Admin created for user ID '{admin.id}' by admin '{current_admin.email}'.")
        return {"message": "Admin created successfully", "admin_id": admin.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/")
async def list_admins(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Any admin can list admins
):
    """
    List all admins.
    """
    try:
        admins = await db.execute(select(Admin))
        return admins.scalars().all()
    except Exception as e:
        logger.error(f"Error listing admins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/sub-role")
async def get_admin_sub_role(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):

    admin = await db.execute(
        select(Admin).filter(Admin.id == current_user.id)
    )
    admin = admin.scalars().first()

    if not admin or not admin.role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin sub-role not found",
        )

    return {"admin_sub_role": admin.role.name}


@router.get("/{admin_id}")
async def get_admin(
    admin_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)  # Any admin can view admins
):
    """
    Get details of a specific admin.
    """
    try:
        admin = await db.execute(select(Admin).filter(Admin.id == admin_id))
        admin = admin.scalars().first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        return admin
    except Exception as e:
        logger.error(f"Error fetching admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{admin_id}")
async def update_admin(
    admin_id: str,
    admin_data: AdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_superadmin)  # Superadmin can update admins
):
    """
    Update an admin.
    """
    try:
        admin = await db.execute(select(Admin).filter(Admin.id == admin_id))
        admin = admin.scalars().first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        # Update admin fields
        if admin_data.role_id:
            admin.role_id = admin_data.role_id

        await db.commit()
        logger.info(f"Admin '{admin.id}' updated by admin '{current_admin.email}'.")
        return {"message": "Admin updated successfully"}
    except Exception as e:
        logger.error(f"Error updating admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(
    admin_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_superadmin)  # Superadmin can delete admins
):
    """
    Delete an admin.
    """
    try:
        admin = await db.execute(select(Admin).filter(Admin.id == admin_id))
        admin = admin.scalars().first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        await db.delete(admin)
        await db.commit()
        logger.info(f"Admin '{admin.id}' deleted by admin '{current_admin.email}'.")
    except Exception as e:
        logger.error(f"Error deleting admin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )