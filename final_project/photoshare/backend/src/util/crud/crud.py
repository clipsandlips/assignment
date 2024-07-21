import bcrypt
from sqlalchemy.orm import Session
from backend.src.util.schemas import schemas
#from backend import models
from backend.src.util.models import models

dbg = True

def get_user(db: Session, user_id: int):
    if dbg: print('get_user')
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    if dbg: print('get_user_by_email')
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    if dbg: print('get_users')
    return db.query(models.User).offset(skip).limit(limit).all()

def hash_password(password: str) -> str:
    if dbg: print('hash_password')
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if dbg: print('verify_password')
    # Verify the given password against the stored hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(db: Session, user: schemas.UserCreate):
    if dbg: print('create_user')
    hashed_password = hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_tags(db, skip: int = 0, limit: int = 10):
    if dbg: print('get_tags')
    return db.query(models.Tag).offset(skip).limit(limit).all()

def get_tag_by_name(db: Session, name: str):
    if dbg: print('get_tag_by_name')
    return db.query(models.Tag).filter(models.Tag.name == name).first()

def create_tag(db: Session, tag: schemas.TagCreate):
    if dbg: print('create_tag')
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag



def create_photo(db: Session, photo: schemas.PhotoCreate, user_id: int):
    print('create_photo')
    db_photo = models.Photo(
        url=photo.url,
        description=photo.description,
        owner_id=user_id
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    print('commit test')

    print(photo.tags)

    for tag_create in photo.tags or []:
        tag_name = tag_create.name  # Access the tag name from TagCreate
        db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not db_tag:
            db_tag = models.Tag(name=tag_name)
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        db_photo.tags.append(db_tag)
        db.commit()

    # Return a response model with tag names
    response_photo = schemas.Photo(
        id=db_photo.id,
        url=db_photo.url,
        description=db_photo.description,
        owner_id=db_photo.owner_id,
        tags=[tag.name for tag in db_photo.tags]
    )

    print('crate_photo completed')
    return response_photo