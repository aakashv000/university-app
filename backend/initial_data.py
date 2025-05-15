import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.core.security import get_password_hash
from app.models.user import User, Role
from app.models.finance import Semester, FeeStructure, StudentFee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_roles(db: Session) -> None:
    roles = [
        {"name": "admin", "description": "Administrator role"},
        {"name": "faculty", "description": "Faculty role"},
        {"name": "student", "description": "Student role"},
    ]
    
    for role_data in roles:
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not role:
            role = Role(**role_data)
            db.add(role)
            logger.info(f"Created role: {role_data['name']}")
    
    db.commit()

def init_users(db: Session) -> None:
    # Get roles
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    faculty_role = db.query(Role).filter(Role.name == "faculty").first()
    student_role = db.query(Role).filter(Role.name == "student").first()
    
    # Create admin user
    admin = db.query(User).filter(User.email == "admin@university.edu").first()
    if not admin:
        admin = User(
            email="admin@university.edu",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_active=True,
        )
        admin.roles.append(admin_role)
        db.add(admin)
        logger.info("Created admin user")
    
    # Create faculty user
    faculty = db.query(User).filter(User.email == "faculty@university.edu").first()
    if not faculty:
        faculty = User(
            email="faculty@university.edu",
            hashed_password=get_password_hash("faculty123"),
            full_name="Faculty User",
            is_active=True,
        )
        faculty.roles.append(faculty_role)
        db.add(faculty)
        logger.info("Created faculty user")
    
    # Create student users
    students = [
        {"email": "student1@university.edu", "full_name": "John Doe"},
        {"email": "student2@university.edu", "full_name": "Jane Smith"},
    ]
    
    for student_data in students:
        student = db.query(User).filter(User.email == student_data["email"]).first()
        if not student:
            student = User(
                email=student_data["email"],
                hashed_password=get_password_hash("student123"),
                full_name=student_data["full_name"],
                is_active=True,
            )
            student.roles.append(student_role)
            db.add(student)
            logger.info(f"Created student user: {student_data['full_name']}")
    
    db.commit()

def init_semesters(db: Session) -> None:
    # Create semesters
    semesters = [
        {
            "name": "Fall 2024",
            "start_date": datetime(2024, 9, 1),
            "end_date": datetime(2024, 12, 15),
        },
        {
            "name": "Spring 2025",
            "start_date": datetime(2025, 1, 15),
            "end_date": datetime(2025, 5, 30),
        },
    ]
    
    for semester_data in semesters:
        semester = db.query(Semester).filter(Semester.name == semester_data["name"]).first()
        if not semester:
            semester = Semester(**semester_data)
            db.add(semester)
            logger.info(f"Created semester: {semester_data['name']}")
    
    db.commit()

def init_fee_structures(db: Session) -> None:
    # Get semesters
    fall_semester = db.query(Semester).filter(Semester.name == "Fall 2024").first()
    spring_semester = db.query(Semester).filter(Semester.name == "Spring 2025").first()
    
    if not fall_semester or not spring_semester:
        logger.error("Semesters not found")
        return
    
    # Create fee structures
    fee_structures = [
        {
            "semester_id": fall_semester.id,
            "name": "Tuition Fee",
            "amount": 5000.00,
            "description": "Regular tuition fee for Fall 2024",
        },
        {
            "semester_id": spring_semester.id,
            "name": "Tuition Fee",
            "amount": 5000.00,
            "description": "Regular tuition fee for Spring 2025",
        },
        {
            "semester_id": fall_semester.id,
            "name": "Hostel Fee",
            "amount": 2000.00,
            "description": "Hostel accommodation fee for Fall 2024",
        },
        {
            "semester_id": spring_semester.id,
            "name": "Hostel Fee",
            "amount": 2000.00,
            "description": "Hostel accommodation fee for Spring 2025",
        },
    ]
    
    for fee_data in fee_structures:
        fee = db.query(FeeStructure).filter(
            FeeStructure.semester_id == fee_data["semester_id"],
            FeeStructure.name == fee_data["name"]
        ).first()
        
        if not fee:
            fee = FeeStructure(**fee_data)
            db.add(fee)
            logger.info(f"Created fee structure: {fee_data['name']} for semester {fee_data['semester_id']}")
    
    db.commit()

def init_student_fees(db: Session) -> None:
    # Get students
    students = db.query(User).join(User.roles).filter(Role.name == "student").all()
    
    # Get semesters
    fall_semester = db.query(Semester).filter(Semester.name == "Fall 2024").first()
    spring_semester = db.query(Semester).filter(Semester.name == "Spring 2025").first()
    
    if not students or not fall_semester or not spring_semester:
        logger.error("Students or semesters not found")
        return
    
    # Create student fees
    for student in students:
        # Fall semester fee
        fall_fee = db.query(StudentFee).filter(
            StudentFee.student_id == student.id,
            StudentFee.semester_id == fall_semester.id
        ).first()
        
        if not fall_fee:
            # Different fees for different students (for demonstration)
            amount = 4500.00 if student.id % 2 == 0 else 5000.00
            
            fall_fee = StudentFee(
                student_id=student.id,
                semester_id=fall_semester.id,
                amount=amount,
                description=f"Tuition fee for {student.full_name} - Fall 2024"
            )
            db.add(fall_fee)
            logger.info(f"Created student fee for {student.full_name} - Fall 2024")
        
        # Spring semester fee
        spring_fee = db.query(StudentFee).filter(
            StudentFee.student_id == student.id,
            StudentFee.semester_id == spring_semester.id
        ).first()
        
        if not spring_fee:
            # Different fees for different students (for demonstration)
            amount = 4800.00 if student.id % 2 == 0 else 5000.00
            
            spring_fee = StudentFee(
                student_id=student.id,
                semester_id=spring_semester.id,
                amount=amount,
                description=f"Tuition fee for {student.full_name} - Spring 2025"
            )
            db.add(spring_fee)
            logger.info(f"Created student fee for {student.full_name} - Spring 2025")
    
    db.commit()

def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()
    
    # Initialize database tables
    init_db()
    
    # Create initial data
    init_roles(db)
    init_users(db)
    init_semesters(db)
    init_fee_structures(db)
    init_student_fees(db)
    
    logger.info("Initial data created")

if __name__ == "__main__":
    main()
