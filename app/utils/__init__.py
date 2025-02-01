# app/utils/__init__.py

from .security import (
    create_access_token, 
    verify_password, 
    hash_password,
    create_refresh_token,
    verify_refresh_token,
    verify_access_token
)  # Security functions
from .logging_config import logger
from .helpers import *
from .dependencies import (
    get_current_admin,
    get_current_instructor,
    get_current_student,
    get_current_user,
    get_admin_with_permission,
    get_moderator,
    get_superadmin
)
from .seed import (
    initialize_roles_and_permissions,
    seed_superadmin
)