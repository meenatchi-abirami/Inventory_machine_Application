from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email_id: EmailStr
    emp_code: str
    role_id: int
    status: str
    create_by: str
    updated_by: str

class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email_id: EmailStr
    emp_code: str
    role_id: int
    status: str
    updated_by: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email_id: str
    emp_code: str
    role_id: int
    status: str
    create_by: str
    updated_by: str
    create_date: datetime
    last_updated_date: datetime
