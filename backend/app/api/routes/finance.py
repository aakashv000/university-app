from typing import Any, List, Optional
from datetime import datetime
import os
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.orm import joinedload

from app.core.dependencies import get_db, get_admin_user, get_faculty_user, get_student_user, get_current_active_user
from app.models.user import User
from app.models.academic import Institute, Course
from app.models.finance import Semester as SemesterModel, FeeStructure, StudentFee, Payment, Receipt, StandardFee
from app.schemas.finance import (
    Semester as SemesterSchema, SemesterCreate, SemesterUpdate,
    FeeStructure as FeeStructureSchema, FeeStructureCreate, FeeStructureUpdate,
    StudentFee as StudentFeeSchema, StudentFeeCreate, StudentFeeUpdate,
    Payment as PaymentSchema, PaymentCreate, PaymentUpdate,
    Receipt as ReceiptSchema, ReceiptCreate,
    PaymentWithReceipt, StudentFeeWithPayments,
    StandardFee as StandardFeeSchema, StandardFeeCreate, StandardFeeUpdate
)
from app.services.receipt_generator import generate_receipt_pdf

router = APIRouter()

# Semester endpoints
@router.get("/semesters", response_model=List[SemesterSchema])
def read_semesters(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve semesters.
    """
    semesters = db.query(SemesterModel).offset(skip).limit(limit).all()
    return semesters

@router.post("/semesters", response_model=SemesterSchema)
def create_semester(
    *,
    db: Session = Depends(get_db),
    semester_in: SemesterCreate,
    current_user: User = Depends(get_admin_user),
) -> Any:
    """
    Create new semester. Admin only.
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == semester_in.course_id).first()
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this id does not exist",
        )
        
    semester = SemesterModel(
        course_id=semester_in.course_id,
        name=semester_in.name,
        type=semester_in.type,
        order_in_course=semester_in.order_in_course,
        start_date=semester_in.start_date,
        end_date=semester_in.end_date,
    )
    db.add(semester)
    db.commit()
    db.refresh(semester)
    return semester

# Fee Structure endpoints
@router.get("/fee-structures", response_model=List[FeeStructureSchema])
def read_fee_structures(
    db: Session = Depends(get_db),
    semester_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve fee structures.
    """
    query = db.query(FeeStructure)
    if semester_id:
        query = query.filter(FeeStructure.semester_id == semester_id)
    fee_structures = query.offset(skip).limit(limit).all()
    return fee_structures

@router.post("/fee-structures", response_model=FeeStructureSchema)
def create_fee_structure(
    *,
    db: Session = Depends(get_db),
    fee_structure_in: FeeStructureCreate,
    current_user: User = Depends(get_admin_user),
) -> Any:
    """
    Create new fee structure. Admin only.
    """
    semester = db.query(SemesterModel).filter(SemesterModel.id == fee_structure_in.semester_id).first()
    if not semester:
        raise HTTPException(
            status_code=404,
            detail="The semester with this id does not exist",
        )
    
    fee_structure = FeeStructure(
        semester_id=fee_structure_in.semester_id,
        name=fee_structure_in.name,
        amount=fee_structure_in.amount,
        description=fee_structure_in.description,
    )
    db.add(fee_structure)
    db.commit()
    db.refresh(fee_structure)
    return fee_structure

# Standard Fee endpoints
@router.get("/standard-fees", response_model=List[StandardFeeSchema])
def read_standard_fees(
    db: Session = Depends(get_db),
    course_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve standard fees. Admin and faculty can see all.
    """
    # Check if user has admin or faculty role
    is_admin_or_faculty = any(role.name in ["admin", "faculty"] for role in current_user.roles)
    if not is_admin_or_faculty:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to access standard fees",
        )
    
    query = db.query(StandardFee)
    
    # Apply filters if provided
    if course_id:
        query = query.filter(StandardFee.course_id == course_id)
    if semester_id:
        query = query.filter(StandardFee.semester_id == semester_id)
    
    # Join related entities
    query = query.join(Course, StandardFee.course_id == Course.id)
    query = query.join(SemesterModel, StandardFee.semester_id == SemesterModel.id)
    query = query.join(Institute, Course.institute_id == Institute.id)
    
    # Load all related entities
    query = query.options(
        joinedload(StandardFee.course).joinedload(Course.institute),
        joinedload(StandardFee.semester)
    )
    
    standard_fees = query.offset(skip).limit(limit).all()
    return standard_fees

@router.post("/standard-fees", response_model=StandardFeeSchema)
def create_standard_fee(
    *,
    db: Session = Depends(get_db),
    standard_fee_in: StandardFeeCreate,
    current_user: User = Depends(get_admin_user),
) -> Any:
    """
    Create new standard fee. Admin only.
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == standard_fee_in.course_id).first()
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this id does not exist",
        )
    
    # Check if semester exists
    semester = db.query(SemesterModel).filter(SemesterModel.id == standard_fee_in.semester_id).first()
    if not semester:
        raise HTTPException(
            status_code=404,
            detail="The semester with this id does not exist",
        )
    
    # Check if semester belongs to the course
    if semester.course_id != standard_fee_in.course_id:
        raise HTTPException(
            status_code=400,
            detail="The semester does not belong to the specified course",
        )
    
    # Check if a standard fee already exists for this course-semester combination
    existing_fee = db.query(StandardFee).filter(
        StandardFee.course_id == standard_fee_in.course_id,
        StandardFee.semester_id == standard_fee_in.semester_id
    ).first()
    
    if existing_fee:
        raise HTTPException(
            status_code=400,
            detail="A standard fee already exists for this course-semester combination",
        )
    
    standard_fee = StandardFee(
        course_id=standard_fee_in.course_id,
        semester_id=standard_fee_in.semester_id,
        amount=standard_fee_in.amount,
        name=standard_fee_in.name,
        description=standard_fee_in.description,
    )
    db.add(standard_fee)
    db.commit()
    db.refresh(standard_fee)
    return standard_fee

@router.put("/standard-fees/{standard_fee_id}", response_model=StandardFeeSchema)
def update_standard_fee(
    *,
    db: Session = Depends(get_db),
    standard_fee_id: int,
    standard_fee_in: StandardFeeUpdate,
    current_user: User = Depends(get_admin_user),
) -> Any:
    """
    Update standard fee. Admin only.
    """
    standard_fee = db.query(StandardFee).filter(StandardFee.id == standard_fee_id).first()
    if not standard_fee:
        raise HTTPException(
            status_code=404,
            detail="Standard fee not found",
        )
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == standard_fee_in.course_id).first()
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this id does not exist",
        )
    
    # Check if semester exists
    semester = db.query(SemesterModel).filter(SemesterModel.id == standard_fee_in.semester_id).first()
    if not semester:
        raise HTTPException(
            status_code=404,
            detail="The semester with this id does not exist",
        )
    
    # Check if semester belongs to the course
    if semester.course_id != standard_fee_in.course_id:
        raise HTTPException(
            status_code=400,
            detail="The semester does not belong to the specified course",
        )
    
    # Check if updating to a combination that already exists (excluding this record)
    if (standard_fee.course_id != standard_fee_in.course_id or 
        standard_fee.semester_id != standard_fee_in.semester_id):
        existing_fee = db.query(StandardFee).filter(
            StandardFee.course_id == standard_fee_in.course_id,
            StandardFee.semester_id == standard_fee_in.semester_id,
            StandardFee.id != standard_fee_id
        ).first()
        
        if existing_fee:
            raise HTTPException(
                status_code=400,
                detail="A standard fee already exists for this course-semester combination",
            )
    
    # Update fields
    for field in standard_fee_in.__dict__:
        if field != "id" and hasattr(standard_fee, field):
            setattr(standard_fee, field, getattr(standard_fee_in, field))
    
    db.commit()
    db.refresh(standard_fee)
    return standard_fee

@router.delete("/standard-fees/{standard_fee_id}", status_code=204, response_model=None)
def delete_standard_fee(
    *,
    db: Session = Depends(get_db),
    standard_fee_id: int,
    current_user: User = Depends(get_admin_user),
) -> None:
    """
    Delete standard fee. Admin only.
    """
    standard_fee = db.query(StandardFee).filter(StandardFee.id == standard_fee_id).first()
    if not standard_fee:
        raise HTTPException(
            status_code=404,
            detail="Standard fee not found",
        )
    
    db.delete(standard_fee)
    db.commit()

# Student Fee endpoints
@router.get("/student-fees", response_model=List[StudentFeeSchema])
def read_student_fees(
    db: Session = Depends(get_db),
    student_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve student fees. Admin and faculty can see all, students can only see their own.
    """
    query = db.query(StudentFee)
    
    # Determine user role
    is_admin = any(role.name == "admin" for role in current_user.roles)
    is_student = any(role.name == "student" for role in current_user.roles)
    
    # Filter by student_id if provided or if current user is a student
    if student_id:
        query = query.filter(StudentFee.student_id == student_id)
    elif is_student:
        query = query.filter(StudentFee.student_id == current_user.id)
    # Admin can see all student fees
    
    # Filter by semester_id if provided
    if semester_id:
        query = query.filter(StudentFee.semester_id == semester_id)
    
    # Join related entities for complete information
    query = query.join(SemesterModel, StudentFee.semester_id == SemesterModel.id)
    query = query.join(Course, StudentFee.course_id == Course.id)
    query = query.join(Institute, Course.institute_id == Institute.id)
    query = query.join(User, StudentFee.student_id == User.id)
    
    # Load all related entities
    query = query.options(
        joinedload(StudentFee.semester),
        joinedload(StudentFee.course).joinedload(Course.institute),
        joinedload(StudentFee.student)
    )
    
    student_fees = query.offset(skip).limit(limit).all()
    return student_fees

@router.post("/student-fees", response_model=StudentFeeSchema)
def create_student_fee(
    *,
    db: Session = Depends(get_db),
    student_fee_in: StudentFeeCreate,
    current_user: User = Depends(get_admin_user),
) -> Any:
    """
    Create new student fee. Admin only.
    """
    # Check if student exists
    student = db.query(User).filter(User.id == student_fee_in.student_id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail="The student with this id does not exist",
        )
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == student_fee_in.course_id).first()
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this id does not exist",
        )
    
    # Check if semester exists
    semester = db.query(SemesterModel).filter(SemesterModel.id == student_fee_in.semester_id).first()
    if not semester:
        raise HTTPException(
            status_code=404,
            detail="The semester with this id does not exist",
        )
    
    # Check if semester belongs to the course
    if semester.course_id != student_fee_in.course_id:
        raise HTTPException(
            status_code=400,
            detail="The semester does not belong to the specified course",
        )
    
    # Check if student is enrolled in the course
    if course not in student.courses:
        raise HTTPException(
            status_code=400,
            detail="The student is not enrolled in this course",
        )
    
    # If amount is not provided, try to get it from standard fee
    amount = student_fee_in.amount
    description = student_fee_in.description
    
    if amount is None:
        # Look up the standard fee for this course-semester combination
        standard_fee = db.query(StandardFee).filter(
            StandardFee.course_id == student_fee_in.course_id,
            StandardFee.semester_id == student_fee_in.semester_id
        ).first()
        
        if standard_fee:
            amount = standard_fee.amount
            description = description or standard_fee.description
        else:
            raise HTTPException(
                status_code=400,
                detail="No amount provided and no standard fee found for this course-semester combination",
            )
    
    student_fee = StudentFee(
        student_id=student_fee_in.student_id,
        course_id=student_fee_in.course_id,
        semester_id=student_fee_in.semester_id,
        amount=amount,
        description=description,
    )
    db.add(student_fee)
    db.commit()
    db.refresh(student_fee)
    return student_fee

# Payment endpoints
@router.get("/payments", response_model=List[PaymentWithReceipt])
def read_payments(
    db: Session = Depends(get_db),
    student_id: Optional[int] = None,
    student_fee_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve payments with filtering options.
    """
    query = db.query(Payment)
    
    # Determine user role
    is_admin = any(role.name == "admin" for role in current_user.roles)
    is_faculty = any(role.name == "faculty" for role in current_user.roles)
    is_student = any(role.name == "student" for role in current_user.roles)
    
    # Filter by student_id if provided
    if student_id:
        query = query.filter(Payment.student_id == student_id)
    # If user is a student and no specific student_id is provided, show only their own payments
    elif is_student and not (is_admin or is_faculty):
        query = query.filter(Payment.student_id == current_user.id)
    # Admin and faculty can see all payments if no student_id filter is provided
    
    # Apply other filters
    if student_fee_id:
        query = query.filter(Payment.student_fee_id == student_fee_id)
    if start_date:
        query = query.filter(Payment.payment_date >= start_date)
    if end_date:
        query = query.filter(Payment.payment_date <= end_date)
    
    # Get payments with joined student_fee data including course and institute
    query = query.join(StudentFee, Payment.student_fee_id == StudentFee.id)
    query = query.join(SemesterModel, StudentFee.semester_id == SemesterModel.id)
    query = query.join(Course, StudentFee.course_id == Course.id)
    query = query.join(Institute, Course.institute_id == Institute.id)
    
    # Load all related entities
    query = query.options(
        joinedload(Payment.student_fee)
        .joinedload(StudentFee.semester),
        joinedload(Payment.student_fee)
        .joinedload(StudentFee.course)
        .joinedload(Course.institute)
    )
    
    payments = query.order_by(desc(Payment.payment_date)).offset(skip).limit(limit).all()
    return payments

@router.post("/payments", response_model=PaymentWithReceipt)
def create_payment(
    *,
    db: Session = Depends(get_db),
    payment_in: PaymentCreate,
    current_user: User = Depends(get_admin_user),
) -> Any:
    """
    Create new payment and generate receipt. Admin only.
    """
    # Check if student exists
    student = db.query(User).filter(User.id == payment_in.student_id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail="The student with this id does not exist",
        )
    
    # Check if student fee exists
    student_fee = db.query(StudentFee).filter(StudentFee.id == payment_in.student_fee_id).first()
    if not student_fee:
        raise HTTPException(
            status_code=404,
            detail="The student fee with this id does not exist",
        )
    
    # Create payment
    payment = Payment(
        student_id=payment_in.student_id,
        student_fee_id=payment_in.student_fee_id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        transaction_id=payment_in.transaction_id,
        notes=payment_in.notes,
    )
    db.add(payment)
    db.flush()
    
    # Get course and semester information for receipt number
    course = student_fee.course
    semester = student_fee.semester
    course_code = course.code.upper()
    semester_code = semester.name.replace(' ', '').upper()
    
    # Generate receipt number with course code and semester info
    receipt_number = f"RCPT-{payment.id}-{course_code}-{semester_code}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create receipt record (without generating PDF)
    receipt = Receipt(
        payment_id=payment.id,
        receipt_number=receipt_number
    )
    db.add(receipt)
    db.commit()
    db.refresh(payment)
    
    return payment

@router.get("/receipts/{receipt_id}/download")
def download_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Download receipt PDF.
    """
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found",
        )
    
    # Check permissions
    payment = db.query(Payment).filter(Payment.id == receipt.payment_id).first()
    is_admin_or_faculty = any(role.name in ["admin", "faculty"] for role in current_user.roles)
    is_student_owner = payment.student_id == current_user.id
    
    if not (is_admin_or_faculty or is_student_owner):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to access this receipt",
        )
    
    # Generate the receipt PDF on-the-fly
    try:
        # Get the necessary data to generate the receipt
        payment = db.query(Payment).filter(Payment.id == receipt.payment_id).first()
        student = db.query(User).filter(User.id == payment.student_id).first()
        student_fee = db.query(StudentFee).filter(StudentFee.id == payment.student_fee_id).first()
        
        # Generate the receipt PDF in memory
        pdf_buffer = generate_receipt_pdf(
            payment=payment,
            student=student,
            student_fee=student_fee,
            receipt_number=receipt.receipt_number
        )
        
        # Return the PDF directly from memory
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                'Content-Disposition': f'attachment; filename="receipt-{receipt.id}.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating receipt: {str(e)}",
        )

@router.get("/students/{student_id}/receipts")
def get_all_student_receipts(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all receipts for a student.
    """
    # Check permissions
    is_admin_or_faculty = any(role.name in ["admin", "faculty"] for role in current_user.roles)
    is_student_owner = current_user.id == student_id
    
    if not (is_admin_or_faculty or is_student_owner):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to access these receipts",
        )
    
    # Get all payments for the student
    payments = db.query(Payment).filter(Payment.student_id == student_id).all()
    receipt_ids = [payment.receipt.id for payment in payments if payment.receipt]
    
    return {"receipt_ids": receipt_ids}

@router.get("/finance/summary")
def get_finance_summary(
    db: Session = Depends(get_db),
    student_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_faculty_user),
) -> Any:
    """
    Get financial summary with filtering options. Faculty and admin only.
    """
    # Query student fees
    fee_query = db.query(StudentFee)
    if student_id:
        fee_query = fee_query.filter(StudentFee.student_id == student_id)
    if semester_id:
        fee_query = fee_query.filter(StudentFee.semester_id == semester_id)
    
    student_fees = fee_query.all()
    
    # Query payments
    payment_query = db.query(Payment)
    if student_id:
        payment_query = payment_query.filter(Payment.student_id == student_id)
    if start_date:
        payment_query = payment_query.filter(Payment.payment_date >= start_date)
    if end_date:
        payment_query = payment_query.filter(Payment.payment_date <= end_date)
    
    payments = payment_query.all()
    
    # Calculate summary
    total_fees = sum(fee.amount for fee in student_fees)
    total_paid = sum(payment.amount for payment in payments)
    total_pending = total_fees - total_paid
    
    return {
        "total_fees": total_fees,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "student_count": len(set(fee.student_id for fee in student_fees)),
        "payment_count": len(payments),
    }
