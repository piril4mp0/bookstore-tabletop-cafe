from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserPublic(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, examples="abcuser")
    full_name: Optional[str] = Field(..., examples="John Doe")
    email: EmailStr = Field(..., examples="abc@gmail.com")


class UserCreate(UserPublic):
    password: str = Field(..., min_length=6, examples="123456")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples="abc@gmail.com")
    password: str = Field(..., min_length=6, examples="123456")


class UserPut(BaseModel):
    username: Optional[str] = Field(
        None, min_length=3, max_length=20, examples="abcuser"
    )
    full_name: Optional[str] = Field(None, examples="John Doe")
    email: Optional[EmailStr] = Field(None, examples="abc@gmail.com")
    password: Optional[str] = Field(None, min_length=6, examples="123456")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
