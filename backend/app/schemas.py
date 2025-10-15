from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    class Config:
        orm_mode = True

class CourseCreate(BaseModel):
    title: str
    description: str
    category: str

class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    class Config:
        orm_mode = True

class ProgressCreate(BaseModel):
    user_id: int
    course_id: int
    completion_percentage: float = 0.0
    status: str = "Not Started"

class ProgressResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    completion_percentage: float
    status: str
    class Config:
        orm_mode = True
