from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_admin_user, get_current_active_user
from app.models.user import User
from app.models.academic import Institute, Course
from app.schemas.academic import (
    Institute as InstituteSchema,
    InstituteCreate, InstituteUpdate,
    Course as CourseSchema,
    CourseCreate, CourseUpdate,
    CourseWithInstitute, InstituteWithCourses
)

router = APIRouter()

# Institute endpoints
@router.get("/institutes", response_model=List[InstituteSchema])
def read_institutes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve institutes.
    """
    institutes = db.query(Institute).offset(skip).limit(limit).all()
    return institutes

@router.post("/institutes", response_model=InstituteSchema)
def create_institute(
    *,
    db: Session = Depends(get_db),
    institute_in: InstituteCreate,
    current_user: User = Depends(get_admin_user),
) -> Any:
    """
    Create new institute. Admin only.
    """
    institute = Institute(
        name=institute_in.name,
        code=institute_in.code,
        description=institute_in.description,
    )
    db.add(institute)
    db.commit()
    db.refresh(institute)
    return institute

@router.get("/institutes/{institute_id}", response_model=InstituteWithCourses)
def read_institute(
    institute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get institute by ID.
    """
    institute = db.query(Institute).filter(Institute.id == institute_id).first()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")
    return institute

# Course endpoints
@router.get("/courses", response_model=List[CourseWithInstitute])
def read_courses(
    db: Session = Depends(get_db),
    institute_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve courses with optional filtering by institute.
    """
    query = db.query(Course)
    if institute_id:
        query = query.filter(Course.institute_id == institute_id)
    courses = query.offset(skip).limit(limit).all()
    return courses

@router.post("/courses", response_model=CourseSchema)
def create_course(
    *,
    db: Session = Depends(get_db),
    course_in: CourseCreate,
    current_user: User = Depends(get_admin_user),
) -> Any:
    """
    Create new course. Admin only.
    """
    # Check if institute exists
    institute = db.query(Institute).filter(Institute.id == course_in.institute_id).first()
    if not institute:
        raise HTTPException(
            status_code=404,
            detail="The institute with this id does not exist",
        )
    
    course = Course(
        institute_id=course_in.institute_id,
        name=course_in.name,
        code=course_in.code,
        duration_years=course_in.duration_years,
        description=course_in.description,
        is_active=course_in.is_active,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.get("/courses/{course_id}", response_model=CourseWithInstitute)
def read_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get course by ID.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.post("/courses/{course_id}/enroll/{student_id}")
def enroll_student(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> Any:
    """
    Enroll a student in a course. Admin only.
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if student exists
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if student has the student role
    if not any(role.name == "student" for role in student.roles):
        raise HTTPException(status_code=400, detail="User is not a student")
    
    # Check if student is already enrolled
    if course in student.courses:
        raise HTTPException(status_code=400, detail="Student already enrolled in this course")
    
    # Enroll student
    student.courses.append(course)
    db.commit()
    
    return {"message": f"Student {student_id} enrolled in course {course_id}"}
