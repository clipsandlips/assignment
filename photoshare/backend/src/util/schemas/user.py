from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None        

class BlacklistedToken(BaseModel):
    token: str
    blacklisted_on: datetime

class UserBase(BaseModel):
    email: str
    disabled: bool

class UserCreate(UserBase):
    email: str
    password: str
    role: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True #orm_mode = True