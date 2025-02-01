# app/routers/__init__.py

from .auth import router as auth_router
from .admin import router as admin_router
from .user import router as user_router
from .course import router as course_router
from .assignment import router as assignment_router
from .discussion import router as discussion_router
from .payment import router as payment_router
from .analytics import router as analytics_router
from .notification import router as notification_router
from .background_task import router as background_task_router
