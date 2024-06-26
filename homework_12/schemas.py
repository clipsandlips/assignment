from pydantic import BaseModel, EmailStr, constr, condate
from typing import Optional, List, Dict
from datetime import date

class ContactBase(BaseModel):
    first_name: Optional[constr(min_length=1, max_length=100)] = None
    last_name: Optional[constr(min_length=1, max_length=100)] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[constr(min_length=10, max_length=15)] = None
    birth_date: Optional[constr(min_length=10, max_length=10)] = None
    additional_info: Optional[str] = None


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: str
    additional_info: str
    owner_id: int

class ContactUpdate(ContactBase):
    pass

class Contact(ContactBase):
    id: int
    owner_id: int

    class Config:
        orm_mode: True

class UserBase(BaseModel):
    username: constr(min_length=1, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    password: constr(min_length=8, max_length=100)

class User(UserBase):
    id: int
    contacts: List[Contact] = []

    class Config:
        orm_mode: True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
