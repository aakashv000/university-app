from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql import func

from app.db.session import Base
# Import only what's needed to avoid circular imports
from app.models.associations import student_course

class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'semester' or 'year'
    order_in_course = Column(Integer, nullable=False)  # e.g., 1st semester, 2nd year
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="semesters")
    fee_structures = relationship("FeeStructure", back_populates="semester")
    student_fees = relationship("StudentFee", back_populates="semester")

class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    semester = relationship("Semester", back_populates="fee_structures")

class StandardFee(Base):
    __tablename__ = "standard_fees"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    amount = Column(Float, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course")
    semester = relationship("Semester")
    
    # Composite unique constraint to ensure only one standard fee per course-semester
    __table_args__ = (
        UniqueConstraint('course_id', 'semester_id', name='uix_standard_fee_course_semester'),
    )

class StudentFee(Base):
    __tablename__ = "student_fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    amount = Column(Float, nullable=True)  # Made nullable to support using standard fees
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("User", back_populates="student_fees")
    course = relationship("Course", back_populates="student_fees")
    semester = relationship("Semester", back_populates="student_fees")
    payments = relationship("Payment", back_populates="student_fee")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_fee_id = Column(Integer, ForeignKey("student_fees.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    payment_method = Column(String, nullable=False)
    transaction_id = Column(String, unique=True)
    notes = Column(Text)
    
    # Relationships
    student = relationship("User", back_populates="payments")
    student_fee = relationship("StudentFee", back_populates="payments")
    receipt = relationship("Receipt", back_populates="payment", uselist=False)

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), unique=True, nullable=False)
    receipt_number = Column(String, unique=True, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    payment = relationship("Payment", back_populates="receipt")
