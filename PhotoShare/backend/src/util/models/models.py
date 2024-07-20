import sys
import os

# Adjust the sys.path to include the backend/src directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src')))

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from util.database import Base

# Define the many-to-many relationship table
photo_tag = Table(
    'photo_tag', Base.metadata,
    Column('photo_id', Integer, ForeignKey('photos.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
    extend_existing=True
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('email', name='uq_users_email'),
        {'extend_existing': True}
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    role = Column(String)

    photos = relationship("Photo", back_populates="owner")



class Photo(Base):
    __tablename__ = "photos"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="photos")
    tags = relationship("Tag", secondary=photo_tag, back_populates="photos")

class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    photos = relationship("Photo", secondary=photo_tag, back_populates="tags")

class TransformedImage(Base):
    __tablename__ = "transformed_images"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    original_photo_id = Column(Integer, ForeignKey("photos.id"))
    transformed_url = Column(String)
    qr_code_url = Column(String)
