from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Institute schemas
class InstituteBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class InstituteCreate(InstituteBase):
    pass

class InstituteUpdate(InstituteBase):
    pass

class InstituteInDBBase(InstituteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Institute(InstituteInDBBase):
    pass

# Course schemas
class CourseBase(BaseModel):
    institute_id: int
    name: str
    code: str
    duration_years: int
    description: Optional[str] = None
    is_active: Optional[bool] = True

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class CourseInDBBase(CourseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Course(CourseInDBBase):
    institute: Institute

# Combined schemas for API responses
class CourseWithInstitute(Course):
    pass

class InstituteWithCourses(Institute):
    courses: List[Course] = []
