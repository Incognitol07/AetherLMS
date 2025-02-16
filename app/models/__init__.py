# app/models/__init__.py

from .user import User
from .admin import Admin, Role
from .course import Course, CourseStatus
from .module import Module
from .assignment import Assignment
from .student import Student
from .enrollment import Enrollment, EnrollmentStatus
from .analytics import Analytics
from .instructor import Instructor
from .comment import Comment
from .discussion import Discussion
from .background_task import BackgroundTask, BackgroundTaskType
from .lesson import Lesson
from .notification import Notification, NotificationType
from .payment import Payment
from .submission import Submission
from .permission import Permission
from .association_tables import course_instructors, role_permission