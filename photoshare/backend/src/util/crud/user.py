import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from backend.src.util.schemas import user as schema_user
from backend.src.util.models import user as model_user
from backend.src.util.crud import token as crud_token
from backend.src.config.jwt import create_access_token
from backend.src.util.logging_config import logger


async def get_user(db: Session, user_id: int):
    logger.debug('get_user')
    result = await db.execute(
                 db.query(model_user.User).filter(model_user.User.id == user_id).first()
    )
    return result

async def get_user_by_email(db: Session, email: str):
    logger.debug('get_user_by_email')
    result = await db.execute( 
                db.query(model_user.User).filter(model_user.User.email == email).first()
    )
    return result

async def get_users(db: Session, skip: int = 0, limit: int = 100):
    logger.debug('get_users')
    result = await db.execute(
             db.query(model_user.User).offset(skip).limit(limit).all()
         )
    return result

def hash_password(password: str) -> str:
    logger.debug('hash_password')
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.debug('verify_password')
    # Verify the given password against the stored hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def create_user(db: Session, user: schema_user.UserCreate):
    logger.debug('create_user')
    hashed_password = hash_password(user.password)
    db_user = model_user.User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    access_token = await create_access_token(data={"sub": db_user.email}, user_id=db_user.id, db=db)
   
    return db_user

async def update_user(db: Session, user: model_user.User, user_update: schema_user.UserUpdate):
    logger.debug('update_user')
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = hash_password(user_update.password)
    if user_update.role is not None:
        user.role = user_update.role
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: Session, user_id: int):
    logger.debug('crud: delete_user')
    try:
        user = db.query(model_user.User).filter(model_user.User.id == user_id).one()
        logger.debug('user: {}'.format(user))
        
        active_tokens = crud_token.get_active_tokens_for_user(db, user_id) 
        #print(active_tokens)

        for token in active_tokens:
            logger.debug('TEST token: {}'.format(token.token))
            crud_token.add_token_to_blacklist(db, token.token)
        
        logger.debug('delete')
        await db.delete(user)
        await db.commit()
    except NoResultFound:
        raise ValueError(f"User with id {user_id} does not exist")
    


