from typing import Any, List, Optional
from datetime import datetime
import os
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.dependencies import get_db, get_admin_user, get_faculty_user, get_student_user, get_current_active_user
from app.models.user import User
from app.models.finance import Semester, FeeStructure, StudentFee, Payment, Receipt
from app.schemas.finance import (
    Semester as SemesterSchema, SemesterCreate, SemesterUpdate,
    FeeStructure as FeeStructureSchema, FeeStructureCreate, FeeStructureUpdate,
    StudentFee as StudentFeeSchema, StudentFeeCreate, StudentFeeUpdate,
    Payment as PaymentSchema, PaymentCreate, PaymentUpdate,
    Receipt as ReceiptSchema, ReceiptCreate,
    PaymentWithReceipt, StudentFeeWithPayments
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
    semesters = db.query(Semester).offset(skip).limit(limit).all()
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
    semester = Semester(
        name=semester_in.name,
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
    semester = db.query(Semester).filter(Semester.id == fee_structure_in.semester_id).first()
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

# Student Fee endpoints
@router.get("/student-fees", response_model=List[StudentFeeSchema])
def read_student_fees(
    db: Session = Depends(get_db),
    student_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_db),
) -> Any:
    """
    Retrieve student fees. Admin and faculty can see all, students can only see their own.
    """
    query = db.query(StudentFee)
    
    # Filter by student_id if provided or if current user is a student
    if student_id:
        query = query.filter(StudentFee.student_id == student_id)
    elif any(role.name == "student" for role in current_user.roles):
        query = query.filter(StudentFee.student_id == current_user.id)
    
    # Filter by semester_id if provided
    if semester_id:
        query = query.filter(StudentFee.semester_id == semester_id)
    
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
    
    # Check if semester exists
    semester = db.query(Semester).filter(Semester.id == student_fee_in.semester_id).first()
    if not semester:
        raise HTTPException(
            status_code=404,
            detail="The semester with this id does not exist",
        )
    
    student_fee = StudentFee(
        student_id=student_fee_in.student_id,
        semester_id=student_fee_in.semester_id,
        amount=student_fee_in.amount,
        description=student_fee_in.description,
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
    current_user: User = Depends(get_db),
) -> Any:
    """
    Retrieve payments with filtering options.
    """
    query = db.query(Payment)
    
    # Filter by student_id if provided or if current user is a student
    if student_id:
        query = query.filter(Payment.student_id == student_id)
    elif any(role.name == "student" for role in current_user.roles):
        query = query.filter(Payment.student_id == current_user.id)
    
    # Apply other filters
    if student_fee_id:
        query = query.filter(Payment.student_fee_id == student_fee_id)
    if start_date:
        query = query.filter(Payment.payment_date >= start_date)
    if end_date:
        query = query.filter(Payment.payment_date <= end_date)
    
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
    
    # Generate receipt number
    receipt_number = f"RCPT-{payment.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Generate PDF path
    pdf_dir = os.path.join(os.getcwd(), "receipts")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"{receipt_number}.pdf")
    
    # Generate receipt PDF
    generate_receipt_pdf(
        payment=payment,
        student=student,
        student_fee=student_fee,
        receipt_number=receipt_number,
        output_path=pdf_path,
    )
    
    # Ensure receipts directory exists
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        
    # Create receipt record
    receipt = Receipt(
        payment_id=payment.id,
        receipt_number=receipt_number,
        pdf_path=pdf_path
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
    
    if not os.path.exists(receipt.pdf_path):
        # If the receipt file doesn't exist, regenerate it
        try:
            # Get the necessary data to regenerate the receipt
            payment = db.query(Payment).filter(Payment.id == receipt.payment_id).first()
            student = db.query(User).filter(User.id == payment.student_id).first()
            student_fee = db.query(StudentFee).filter(StudentFee.id == payment.student_fee_id).first()
            
            # Ensure receipts directory exists
            pdf_dir = os.path.join(os.getcwd(), "receipts")
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
                
            # Regenerate the receipt PDF
            generate_receipt_pdf(
                payment=payment,
                student=student,
                student_fee=student_fee,
                receipt_number=receipt.receipt_number,
                output_path=receipt.pdf_path
            )
            
            if not os.path.exists(receipt.pdf_path):
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate receipt file",
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error regenerating receipt: {str(e)}",
            )
    
    return FileResponse(
        path=receipt.pdf_path,
        filename=f"{receipt.receipt_number}.pdf",
        media_type="application/pdf"
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
