from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import bcrypt

import crud
import models
import schemas
from database import get_db


import os
from itsdangerous import URLSafeTimedSerializer
import aiosmtplib 
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape
import configparser

from settings import settings
import jwt
from fastapi import HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes={"read": "Read access", "write": "Write access"})

#SECRET_KEY = "secret-key-123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        print(f"User not found: {username}")
        return False
    if not verify_password(password, user.hashed_password):
        print(f"Invalid password for user: {username}")
        return False
    return user

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:  # Use JWTError from jose.exceptions
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



# Load configuration from config.ini file
#file_config = 'db_psql_config.ini'
#config = configparser.ConfigParser()
#config.read(file_config)

#sections = config.sections()
#print(f"Sections found: {sections}")

if hasattr(settings, "smtp_username") and hasattr(settings, "smtp_password") and \
   hasattr(settings, "smtp_hostname") :
    smtp_username = settings.smtp_username 
    smtp_password = settings.smtp_password
    smtp_hostname = settings.smtp_hostname
    
if hasattr(settings, "hash_secret_key") and hasattr(settings, "hash_salt") : 
    SECRET_KEY = settings.hash_secret_key   #configs.get('HASH', 'HASH_SECRET_KEY')  
    SALT = settings.hash_salt               #config.get('HASH', 'HASH_SALT')


def generate_confirmation_token(email: str):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SALT)

def confirm_token(token: str, expiration: int = 3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt=SALT, max_age=expiration)
    except Exception:
        return False
    return email

async def send_email(subject: str, recipient: str, html_content: str):
    message = EmailMessage()
    message["From"] = smtp_username
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname= smtp_hostname,
        port=587,
        start_tls=True,
        username=smtp_username,
        password=smtp_password,
    )



env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(['html', 'xml']))
template = env.get_template("email_verification.html")

async def send_verification_email(email: str, token: str):
    verification_url = f"http://127.0.0.1:8000/verify-email?token={token}"
    html_content = template.render(verification_url=verification_url)
    await send_email("Email Verification", email, html_content)


def extract_username_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        print('test233')
        print(payload.get("sub"))
        print('test333')
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token: Email not found")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")