# app/models/__init__.py

from .user import User
from .admin import Admin, Role
from .course import Course
from .module import Module
from .assignment import Assignment
from .student import Student
from .analytics import Analytics
from .instructor import Instructor
from .comment import Comment
from .discussion import Discussion
from .background_task import BackgroundTask
from .lesson import Lesson
from .notification import Notification
from .payment import Payment
from .submission import Submission
from .association_tables import course_instructors  # Add this line