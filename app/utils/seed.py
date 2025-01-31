# app/utils/seed.py

from app.models import Role  # Ensure you import the Role model
from app.database import SessionLocal
from sqlalchemy.future import select

async def initialize_roles():
    async with SessionLocal() as db:
        try:
            # Define roles and their permissions
            roles = [
                Role(
                    name="superadmin",
                    permissions=[
                        "view_reports",
                        "manage_users",
                        "edit_settings",
                        "delete_data",
                        "manage_roles",
                        "manage_admins",
                    ],
                ),
                Role(
                    name="admin",
                    permissions=[
                        "view_reports",
                        "manage_users",
                        "manage_courses",
                        "manage_instructors",
                        "manage_students",
                    ],
                ),
                Role(
                    name="instructor",
                    permissions=[
                        "view_reports",
                        "manage_courses",
                        "manage_assignments",
                        "grade_assignments",
                        "manage_students",
                    ],
                ),
                Role(
                    name="student",
                    permissions=[
                        "view_courses",
                        "submit_assignments",
                        "view_grades",
                        "view_materials",
                    ],
                ),
                Role(
                    name="moderator",
                    permissions=[
                        "view_reports",
                        "manage_content",
                        "manage_comments",
                    ],
                ),
            ]

            # Insert roles into the database if they don't exist
            for role in roles:
                existing_role = await db.execute(
                    (select(Role).filter(Role.name == role.name))
                )
                if not existing_role.scalars().first():
                    db.add(role)
            await db.commit()
        except Exception as e:
            print(f"Error initializing roles: {e}")
            await db.rollback()
        finally:
            await db.close()