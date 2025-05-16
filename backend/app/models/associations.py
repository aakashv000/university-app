"""Association tables for many-to-many relationships.

This module contains all association tables to avoid circular imports.
"""

from sqlalchemy import Column, Integer, ForeignKey, Table
from app.db.session import Base

# Association table for many-to-many relationship between users and roles
user_role = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

# Association table for many-to-many relationship between students and courses
student_course = Table(
    "student_courses",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
)
