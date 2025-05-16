import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.core.security import get_password_hash
from app.models.user import User, Role
from app.models.academic import Institute, Course
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

def init_institutes(db: Session) -> None:
    # Create institutes
    institutes = [
        {
            "name": "School of Engineering",
            "code": "ENG",
            "description": "The School of Engineering offers programs in various engineering disciplines.",
        },
        {
            "name": "School of Business",
            "code": "BUS",
            "description": "The School of Business offers programs in business administration and management.",
        },
    ]
    
    for institute_data in institutes:
        institute = db.query(Institute).filter(Institute.code == institute_data["code"]).first()
        if not institute:
            institute = Institute(**institute_data)
            db.add(institute)
            logger.info(f"Created institute: {institute_data['name']}")
    
    db.commit()
    return db.query(Institute).all()

def init_courses(db: Session, institutes) -> None:
    # Create courses
    eng_institute = next((i for i in institutes if i.code == "ENG"), None)
    bus_institute = next((i for i in institutes if i.code == "BUS"), None)
    
    if not eng_institute or not bus_institute:
        logger.error("Institutes not found")
        return []
    
    courses = [
        {
            "institute_id": eng_institute.id,
            "name": "Bachelor of Computer Science",
            "code": "BCS",
            "duration_years": 4,
            "description": "A comprehensive program covering computer science fundamentals and applications.",
            "is_active": True,
        },
        {
            "institute_id": bus_institute.id,
            "name": "Master of Business Administration",
            "code": "MBA",
            "duration_years": 2,
            "description": "An advanced program for business professionals.",
            "is_active": True,
        },
    ]
    
    for course_data in courses:
        course = db.query(Course).filter(Course.code == course_data["code"]).first()
        if not course:
            course = Course(**course_data)
            db.add(course)
            logger.info(f"Created course: {course_data['name']}")
    
    db.commit()
    return db.query(Course).all()

def init_semesters(db: Session, courses) -> None:
    # Get courses
    bcs_course = next((c for c in courses if c.code == "BCS"), None)
    mba_course = next((c for c in courses if c.code == "MBA"), None)
    
    if not bcs_course or not mba_course:
        logger.error("Courses not found")
        return []
    
    # Create semesters
    semesters = [
        {
            "course_id": bcs_course.id,
            "name": "Fall 2024",
            "type": "semester",
            "order_in_course": 1,
            "start_date": datetime(2024, 8, 15),
            "end_date": datetime(2024, 12, 20),
        },
        {
            "course_id": bcs_course.id,
            "name": "Spring 2025",
            "type": "semester",
            "order_in_course": 2,
            "start_date": datetime(2025, 1, 15),
            "end_date": datetime(2025, 5, 30),
        },
        {
            "course_id": mba_course.id,
            "name": "Year 1",
            "type": "year",
            "order_in_course": 1,
            "start_date": datetime(2024, 8, 15),
            "end_date": datetime(2025, 5, 30),
        },
    ]
    
    for semester_data in semesters:
        # Check for existing semester by course and name
        semester = db.query(Semester).filter(
            Semester.course_id == semester_data["course_id"],
            Semester.name == semester_data["name"]
        ).first()
        
        if not semester:
            semester = Semester(**semester_data)
            db.add(semester)
            logger.info(f"Created semester: {semester_data['name']} for course {semester_data['course_id']}")
    
    db.commit()
    return db.query(Semester).all()

def init_fee_structures(db: Session, semesters) -> None:
    # Get semesters by name and course
    bcs_fall = next((s for s in semesters if s.name == "Fall 2024" and s.type == "semester"), None)
    bcs_spring = next((s for s in semesters if s.name == "Spring 2025" and s.type == "semester"), None)
    mba_year = next((s for s in semesters if s.name == "Year 1" and s.type == "year"), None)
    
    if not bcs_fall or not bcs_spring or not mba_year:
        logger.error("Semesters not found")
        return
    
    # Create fee structures
    fee_structures = [
        {
            "semester_id": bcs_fall.id,
            "name": "Tuition Fee",
            "amount": 5000.00,
            "description": "Regular tuition fee for Computer Science - Fall 2024",
        },
        {
            "semester_id": bcs_spring.id,
            "name": "Tuition Fee",
            "amount": 5000.00,
            "description": "Regular tuition fee for Computer Science - Spring 2025",
        },
        {
            "semester_id": bcs_fall.id,
            "name": "Hostel Fee",
            "amount": 2000.00,
            "description": "Hostel accommodation fee for Computer Science - Fall 2024",
        },
        {
            "semester_id": bcs_spring.id,
            "name": "Hostel Fee",
            "amount": 2000.00,
            "description": "Hostel accommodation fee for Computer Science - Spring 2025",
        },
        {
            "semester_id": mba_year.id,
            "name": "MBA Tuition Fee",
            "amount": 12000.00,
            "description": "Annual tuition fee for MBA program",
        },
        {
            "semester_id": mba_year.id,
            "name": "MBA Materials Fee",
            "amount": 1500.00,
            "description": "Annual fee for MBA course materials and resources",
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

def init_student_fees(db: Session, courses, semesters) -> None:
    # Get students
    students = db.query(User).join(User.roles).filter(Role.name == "student").all()
    
    # Get courses
    bcs_course = next((c for c in courses if c.code == "BCS"), None)
    mba_course = next((c for c in courses if c.code == "MBA"), None)
    
    # Get semesters
    bcs_fall = next((s for s in semesters if s.name == "Fall 2024" and s.type == "semester"), None)
    bcs_spring = next((s for s in semesters if s.name == "Spring 2025" and s.type == "semester"), None)
    mba_year = next((s for s in semesters if s.name == "Year 1" and s.type == "year"), None)
    
    if not students or not bcs_course or not mba_course or not bcs_fall or not bcs_spring or not mba_year:
        logger.error("Students, courses, or semesters not found")
        return
        
    # Enroll students in courses
    for i, student in enumerate(students):
        # Enroll first student in both courses, others alternating
        if i == 0:
            if bcs_course not in student.courses:
                student.courses.append(bcs_course)
                logger.info(f"Enrolled {student.full_name} in {bcs_course.name}")
            if mba_course not in student.courses:
                student.courses.append(mba_course)
                logger.info(f"Enrolled {student.full_name} in {mba_course.name}")
        elif i % 2 == 0:
            if bcs_course not in student.courses:
                student.courses.append(bcs_course)
                logger.info(f"Enrolled {student.full_name} in {bcs_course.name}")
        else:
            if mba_course not in student.courses:
                student.courses.append(mba_course)
                logger.info(f"Enrolled {student.full_name} in {mba_course.name}")
    
    db.commit()
    
    # Create student fees
    for student in students:
        # Create fees based on course enrollment
        for course in student.courses:
            if course.code == "BCS":
                # BCS Fall semester fee
                fall_fee = db.query(StudentFee).filter(
                    StudentFee.student_id == student.id,
                    StudentFee.course_id == bcs_course.id,
                    StudentFee.semester_id == bcs_fall.id
                ).first()
                
                if not fall_fee:
                    # Different fees for different students (for demonstration)
                    amount = 4500.00 if student.id % 2 == 0 else 5000.00
                    
                    fall_fee = StudentFee(
                        student_id=student.id,
                        course_id=bcs_course.id,
                        semester_id=bcs_fall.id,
                        amount=amount,
                        description=f"Computer Science tuition for {student.full_name} - Fall 2024"
                    )
                    db.add(fall_fee)
                    logger.info(f"Created BCS student fee for {student.full_name} - Fall 2024")
                
                # BCS Spring semester fee
                spring_fee = db.query(StudentFee).filter(
                    StudentFee.student_id == student.id,
                    StudentFee.course_id == bcs_course.id,
                    StudentFee.semester_id == bcs_spring.id
                ).first()
                
                if not spring_fee:
                    # Different fees for different students (for demonstration)
                    amount = 4800.00 if student.id % 2 == 0 else 5000.00
                    
                    spring_fee = StudentFee(
                        student_id=student.id,
                        course_id=bcs_course.id,
                        semester_id=bcs_spring.id,
                        amount=amount,
                        description=f"Computer Science tuition for {student.full_name} - Spring 2025"
                    )
                    db.add(spring_fee)
                    logger.info(f"Created BCS student fee for {student.full_name} - Spring 2025")
                    
            elif course.code == "MBA":
                # MBA Year fee
                mba_fee = db.query(StudentFee).filter(
                    StudentFee.student_id == student.id,
                    StudentFee.course_id == mba_course.id,
                    StudentFee.semester_id == mba_year.id
                ).first()
                
                if not mba_fee:
                    # Different fees for different students (for demonstration)
                    amount = 11500.00 if student.id % 2 == 0 else 12000.00
                    
                    mba_fee = StudentFee(
                        student_id=student.id,
                        course_id=mba_course.id,
                        semester_id=mba_year.id,
                        amount=amount,
                        description=f"MBA tuition for {student.full_name} - Year 1"
                    )
                    db.add(mba_fee)
                    logger.info(f"Created MBA student fee for {student.full_name} - Year 1")
    
    db.commit()

def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()
    
    # Initialize database tables
    init_db()
    
    # Create initial data in the correct order
    init_roles(db)
    init_users(db)
    
    # Initialize academic structure
    institutes = init_institutes(db)
    courses = init_courses(db, institutes)
    semesters = init_semesters(db, courses)
    
    # Initialize financial data
    init_fee_structures(db, semesters)
    init_student_fees(db, courses, semesters)
    
    logger.info("Initial data created")

if __name__ == "__main__":
    main()
