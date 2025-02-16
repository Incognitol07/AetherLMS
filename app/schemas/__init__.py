# app/schemas/__init__.py

from .admin import (
    AdminCreate,
    AdminResponse,
    AdminUpdate,
    PermissionUpdate,
    RoleResponse
)

from .auth import(
    LoginResponse,
    UserResponse,
    Token,
    UserCreate
)

from .course import(
    CourseCreate,
    CourseResponse,
    CourseUpdate,
    ModuleCreate,
    ModuleResponse
)