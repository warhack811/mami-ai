from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str # OAuth2 password flow uses username
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    plan_type: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
