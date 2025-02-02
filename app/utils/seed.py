# app/utils/seed.py

from app.models import User, Role, Admin, UserRole, Permission
from app.database import AsyncSessionLocal
from sqlalchemy.future import select
from app.utils import hash_password
from sqlalchemy.sql import func


async def initialize_roles_and_permissions():
    async with AsyncSessionLocal() as db:
        try:
            # Define permissions
            permissions = [
                Permission(name="view_reports"),
                Permission(name="manage_users"),
                Permission(name="edit_settings"),
                Permission(name="delete_data"),
                Permission(name="manage_roles"),
                Permission(name="manage_admins"),
                Permission(name="manage_courses"),
                Permission(name="manage_content"),
                Permission(name="manage_comments"),
                Permission(name="manage_enrollments"),
                Permission(name="manage_assessments"),
                Permission(name="view_analytics"),
                Permission(name="manage_support_tickets"),
                Permission(name="manage_certificates"),
                Permission(name="manage_announcements"),
                Permission(name="manage_discussions"),
            ]

            # Insert permissions into the database if they don't exist
            for perm in permissions:
                existing_perm = await db.execute(
                    select(Permission).filter(Permission.name == perm.name)
                )
                if not existing_perm.scalars().first():
                    db.add(perm)

            # Define roles and their permissions
            roles = [
                Role(name="superadmin"),
                Role(name="admin"),
                Role(name="moderator"),
                Role(name="content_manager"),
                Role(name="support"),
            ]

            # Assign permissions to roles
            roles[0].permissions = permissions  # superadmin has all permissions
            roles[1].permissions = [
                perm
                for perm in permissions
                if perm.name not in ["manage_roles", "manage_admins"]
            ]  # admin
            roles[2].permissions = [
                perm
                for perm in permissions
                if perm.name
                in [
                    "view_reports",
                    "manage_content",
                    "manage_comments",
                    "manage_discussions",
                ]
            ]  # moderator
            roles[3].permissions = [
                perm
                for perm in permissions
                if perm.name
                in ["manage_content", "manage_courses", "manage_announcements"]
            ]  # content manager
            roles[4].permissions = [
                perm
                for perm in permissions
                if perm.name in ["manage_support_tickets", "view_reports"]
            ]  # support

            # Insert roles into the database if they don't exist
            for role in roles:
                existing_role = await db.execute(
                    select(Role).filter(Role.name == role.name)
                )
                if not existing_role.scalars().first():
                    db.add(role)

            await db.commit()
        except Exception as e:
            print(f"Error initializing roles and permissions: {e}")
            await db.rollback()
        finally:
            await db.close()


async def seed_superadmin():
    async with AsyncSessionLocal() as db:
        try:
            # Check if superadmin already exists
            superadmin_email = "superadmin@example.com"
            existing_user = await db.execute(
                select(User).filter(User.email == superadmin_email)
            )
            if existing_user.scalars().first():
                print("Superadmin already exists.")
                return

            # Create the superadmin user
            superadmin = User(
                full_name="Super Admin",
                email=superadmin_email,
                hashed_password=hash_password("superadmin"),
                role=UserRole.ADMIN,  # Primary role is admin
                date_joined=func.now(),
            )
            db.add(superadmin)
            await db.commit()

            # Fetch the superadmin role
            superadmin_role = await db.execute(
                select(Role).filter(Role.name == "superadmin")
            )
            superadmin_role = superadmin_role.scalars().first()

            if not superadmin_role:
                raise Exception(
                    "Superadmin role not found. Please initialize roles first."
                )

            # Assign the superadmin role to the user
            admin = Admin(
                user_id=superadmin.id,
                role_id=superadmin_role.id,
                created_at=func.now(),
                updated_at=func.now(),
            )
            db.add(admin)
            await db.commit()

            print("Superadmin created successfully.")
        except Exception as e:
            print(f"Error seeding superadmin: {e}")
            await db.rollback()
        finally:
            await db.close()
