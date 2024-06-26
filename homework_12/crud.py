from sqlalchemy.orm import Session
import models
import schemas
import auth
from datetime import datetime

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    print(f"birth_date type: {type(contact.birth_date)}")  
    print(f"birth_date value: {contact.birth_date}")  

    db_contact = models.Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birth_date=contact.birth_date, #contact_dict['birth_date'], #birth_date_str, #birth_date,    #contact.birth_date,  # Ensure this is a datetime.date object
        additional_info=contact.additional_info,
        owner_id=user_id
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Contact).filter(models.Contact.owner_id == user_id).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int, user_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()

def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate, user_id: int):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()
    if db_contact:
        for field, value in contact.dict(exclude_unset=True).items():
            setattr(db_contact, field, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact
