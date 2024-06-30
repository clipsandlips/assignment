
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import datetime, timedelta

import models, email_utils, schemas, crud
from auth import authenticate_user, create_access_token, get_current_active_user, SECRET_KEY, ALGORITHM
from database import SessionLocal, engine, get_db
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
#from fastapi.middleware.cors import CORSMiddleware
import aioredis
import configparser
from redis import Redis
from contextlib import asynccontextmanager

import logging

from settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from config.ini file
#file_config = '.env'
#config = configparser.ConfigParser()
#config.read(file_config)

#sections = config.sections()



if hasattr(settings, "cloudinary_cloud_name") and hasattr(settings, "cloudinary_api_key") and \
   hasattr(settings, "cloudinary_api_secret") :

    cd_cloud_name = settings.cloudinary_cloud_name  #config.get('CLOUDINARY', 'CLOUD_NAME') 
    cd_api_key = settings.cloudinary_api_key        # config.get('CLOUDINARY', 'API_KEY')
    cd_api_secret = settings.cloudinary_api_secret  #config.get('CLOUDINARY', 'API_SECRET')



cloudinary.config( 
        cloud_name = cd_cloud_name, 
        api_key = cd_api_key, 
        api_secret = cd_api_secret,
        secure=True
    )


limiter = RateLimiter()

redis_url = "redis://localhost:6379"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager to manage the lifespan of the FastAPI application.
    It connects to Redis and initializes FastAPILimiter.
    """
    redis_client = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)
    
        
    yield  

    await redis_client.close()

app = FastAPI(lifespan=lifespan)

models.Base.metadata.create_all(bind=engine)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000/",
    "http://0.0.0.0:8000/",    
]



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)





@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log incoming requests and outgoing responses.
    """
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response






@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint to obtain an access token for authentication.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)
    
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/refresh-token", response_model=schemas.Token)
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    new_db_user = crud.create_user(db=db, user=user)

    token = crud.generate_verification_token(user.email)
    await email_utils.send_verification_email(user.email, token)
    

    return new_db_user




@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.post("/contacts/", response_model=schemas.Contact, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    try:
        # Your existing logic
        contact = crud.create_contact(db=db, contact=contact, user_id=current_user.id)
        return contact
    except HTTPException as e:
        # Log the exception or handle it appropriately
        print(f"HTTP Exception occurred in create_contact: {e}")
        raise
    except Exception as e:
        # Log other exceptions
        print(f"Exception occurred in create_contact: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
        


@app.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    contacts = crud.get_contacts(db, user_id=current_user.id, skip=skip, limit=limit)
    return contacts

@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.update_contact(db=db, contact_id=contact_id, contact=contact, user_id=current_user.id)

@app.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.delete_contact(db=db, contact_id=contact_id, user_id=current_user.id)

@app.get("/")
def read_root():
    """
    Get the root endpoint.

    Returns:
        dict: A dictionary with a greeting message.
    """
    return {"status": "API is running"}






@app.post("/upload-avatar/", response_model=schemas.User)
async def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    try:
        # Upload file to Cloudinary
        result = cloudinary.uploader.upload(file.file, folder=f"user_avatars/{current_user.id}/")
        
        # Get the secure URL of the uploaded image
        avatar_url = result.get("secure_url")
        
        # Update the user's avatar URL in the database
        current_user.avatar_url = avatar_url
        db.commit()
        db.refresh(current_user)
        
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload avatar: {str(e)}")


@app.get("/verify-email/")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        email = email_utils.confirm_token(token)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
    user = crud.verify_user_email(db, email)
    return {"message": "Email verified successfully"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)