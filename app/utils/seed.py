# app/utils/seed.py

# app/utils/seed.py

from app.models import User, Role, Permission, Admin
from app.database import AsyncSessionLocal
from sqlalchemy.future import select
from app.utils import hash_password


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
                Permission(name="view_courses"),
                Permission(name="participate_in_discussions"),
                Permission(name="submit_assignments"),
                Permission(name="view_grades"),
                Permission(name="grade_assignments"),
            ]

            # Insert permissions into the database if they don't exist
            for perm in permissions:
                existing_perm = await db.execute(
                    select(Permission).filter(Permission.name == perm.name)
                )
                if not existing_perm.scalars().first():
                    db.add(perm)

            # Fetch permissions after inserting
            await db.commit()
            existing_permissions = {perm.name: perm for perm in (await db.execute(select(Permission))).scalars().all()}

            # Define roles and their permissions
            roles = [
                Role(name="superadmin"),
                Role(name="moderator"),
                Role(name="content_manager"),
                Role(name="support"),
                Role(name="student"),
                Role(name="instructor"),
            ]

            # Assign permissions to roles
            roles[0].permissions = list(existing_permissions.values())  # superadmin has all permissions
            roles[1].permissions = [
                existing_permissions.get("view_reports"),
                existing_permissions.get("manage_content"),
                existing_permissions.get("manage_comments"),
                existing_permissions.get("manage_discussions"),
            ]  # moderator
            roles[2].permissions = [
                existing_permissions.get("manage_content"),
                existing_permissions.get("manage_courses"),
                existing_permissions.get("manage_announcements"),
            ]  # content manager
            roles[3].permissions = [
                existing_permissions.get("manage_support_tickets"),
                existing_permissions.get("view_reports"),
            ]  # support
            roles[4].permissions = [
                existing_permissions.get("view_courses"),
                existing_permissions.get("participate_in_discussions"),
                existing_permissions.get("submit_assignments"),
                existing_permissions.get("view_grades"),
            ]  # student
            roles[5].permissions = [
                existing_permissions.get("manage_courses"),
                existing_permissions.get("grade_assignments"),
                existing_permissions.get("manage_enrollments"),
                existing_permissions.get("view_reports"),
            ]  # instructor

            # Insert roles into the database if they don't exist
            for role in roles:
                existing_role = await db.execute(
                    select(Role).filter(Role.name == role.name)
                )
                if not existing_role.scalars().first():
                    db.add(role)

            await db.commit()
            print("Roles and permissions initialized successfully.")

        except Exception as e:
            await db.rollback()
            print(f"Error initializing roles and permissions: {e}")

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

            # Fetch the superadmin role
            superadmin_role = await db.execute(
                select(Role).filter(Role.name == "superadmin")
            )
            superadmin_role = superadmin_role.scalars().first()

            if not superadmin_role:
                raise Exception("Superadmin role not found. Please initialize roles first.")

            # Create the superadmin user
            superadmin = User(
                full_name="Super Admin",
                email=superadmin_email,
                hashed_password=hash_password("superadmin"),
                role=superadmin_role
            )
            db.add(superadmin)
            await db.commit()

            # Create the corresponding Admin entry
            admin = Admin(id=superadmin.id)
            db.add(admin)
            await db.commit()

            print("Superadmin created successfully.")
        except Exception as e:
            print(f"Error seeding superadmin: {e}")
            await db.rollback()
        finally:
            await db.close()
