from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.schemas.academic import Institute, Course
from app.schemas.user import User

# Semester schemas
class SemesterBase(BaseModel):
    course_id: int
    name: str
    type: str  # 'semester' or 'year'
    order_in_course: int
    start_date: datetime
    end_date: datetime

class SemesterCreate(SemesterBase):
    pass

class SemesterUpdate(SemesterBase):
    pass

class SemesterInDBBase(SemesterBase):
    id: int

    class Config:
        orm_mode = True

class Semester(SemesterInDBBase):
    course: Optional[Course] = None

# FeeStructure schemas
class FeeStructureBase(BaseModel):
    semester_id: int
    name: str
    amount: float
    description: Optional[str] = None

class FeeStructureCreate(FeeStructureBase):
    pass

class FeeStructureUpdate(FeeStructureBase):
    pass

class FeeStructureInDBBase(FeeStructureBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class FeeStructure(FeeStructureInDBBase):
    semester: Semester

# StudentFee schemas
class StudentFeeBase(BaseModel):
    student_id: int
    course_id: int
    semester_id: int
    amount: float
    description: Optional[str] = None

class StudentFeeCreate(StudentFeeBase):
    pass

class StudentFeeUpdate(StudentFeeBase):
    pass

class StudentFeeInDBBase(StudentFeeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class StudentFee(StudentFeeInDBBase):
    course: Optional[Course] = None
    semester: Optional[Semester] = None
    student: Optional[User] = None
    
    @property
    def course_name(self) -> str:
        return self.course.name if self.course else "N/A"
        
    @property
    def institute_name(self) -> str:
        return self.course.institute.name if self.course and self.course.institute else "N/A"
        
    @property
    def student_name(self) -> str:
        return self.student.full_name if self.student else "N/A"

# Payment schemas
class PaymentBase(BaseModel):
    student_id: int
    student_fee_id: int
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(PaymentBase):
    pass

class PaymentInDBBase(PaymentBase):
    id: int
    payment_date: datetime

    class Config:
        orm_mode = True

class Payment(PaymentInDBBase):
    pass

# Receipt schemas
class ReceiptBase(BaseModel):
    payment_id: int
    receipt_number: str
    pdf_path: Optional[str] = None

class ReceiptCreate(ReceiptBase):
    pass

class ReceiptUpdate(ReceiptBase):
    pass

class ReceiptInDBBase(ReceiptBase):
    id: int
    generated_at: datetime

    class Config:
        orm_mode = True

class Receipt(ReceiptInDBBase):
    pass

# Combined schemas for API responses
class PaymentWithReceipt(Payment):
    receipt: Optional[Receipt] = None
    student_fee: Optional[StudentFee] = None

class SemesterWithCourse(Semester):
    course: Course

class StudentFeeWithPayments(StudentFee):
    payments: List[PaymentWithReceipt] = []
