"""Models package initialization.

This module imports all models in the correct order to avoid circular imports.
"""

# First, import association tables
from app.models.associations import user_role, student_course

# Then import base models that don't depend on other models
from app.models.user import Role, User

# Then import models that depend on base models
from app.models.academic import Institute, Course

# Finally import models that depend on all previous models
from app.models.finance import Semester, FeeStructure, StudentFee, Payment, Receipt

# This ensures all models are available when importing from app.models
__all__ = [
    'user_role', 'student_course',
    'User', 'Role',
    'Institute', 'Course',
    'Semester', 'FeeStructure', 'StudentFee', 'Payment', 'Receipt'
]
