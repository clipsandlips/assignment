from pydantic import BaseModel
from typing import List, Optional


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None        


class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    role: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True #orm_mode = True

class PhotoBase(BaseModel):
    description: Optional[str] = None

class PhotoCreate(PhotoBase):
    tags: Optional[List[str]] = None

class Photo(PhotoBase):
    id: int
    url: str
    owner_id: int
    tags: List[str] = []

    class Config:
        from_attributes = True #orm_mode = True

class TagBase(BaseModel):
    name: str

class TagCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True #orm_mode = True


class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True #orm_mode = True

class TransformedImageBase(BaseModel):
    original_photo_id: int

class TransformedImageCreate(TransformedImageBase):
    transformed_url: str

class TransformedImage(TransformedImageBase):
    id: int
    transformed_url: str
    qr_code_url: str

    class Config:
        from_attributes = True #orm_mode = True
