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
