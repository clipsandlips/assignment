import sys
import os
import logging

# Adjust the sys.path to include the backend/src directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src')))

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from util.database import Base


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log table creation attempts
logger.info("Defining models and their relationships.")


# Define the many-to-many relationship table
photo_tag = Table(
    'photo_tag', Base.metadata,
    Column('photo_id', Integer, ForeignKey('photos.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
    extend_existing=True
)


class User(Base):
    __tablename__ = "users"

    #id = Column(Integer)
    id = Column(Integer, primary_key=True)
    email = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    role = Column(String)

    #photos = relationship("Photo", back_populates="owner")

    __table_args__ = (
        Index('ix_users_id', 'id', unique=True, postgresql_if_not_exists=True),
        UniqueConstraint('email', name='uq_users_email'),
        {'extend_existing': True}
    )


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
