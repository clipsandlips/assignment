import bcrypt
from sqlalchemy.orm import Session
from backend.src.util.schemas import tag as schema_tag
from backend.src.util.models import tag as model_tag 

from backend.src.util.logging_config import logger
#import logging

def get_tags(db, skip: int = 0, limit: int = 10):
    logger.debug('get_tags')
    return db.query(model_tag.Tag).offset(skip).limit(limit).all()

def get_tag_by_name(db: Session, name: str):
    logger.debug('get_tag_by_name')
    return db.query(model_tag.Tag).filter(model_tag.Tag.name == name).first()

def create_tag(db: Session, tag: schema_tag.TagCreate):
    logger.debug('create_tag')
    db_tag = model_tag.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag
