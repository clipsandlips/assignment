from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from backend.src.util.schemas import schemas
from backend.src.util.models import models
from backend.src.util.crud import crud
from backend.src.config import auth 
from backend.src.config.auth import get_db, get_current_active_user, get_password_hash, create_access_token
from backend.src.config.dependencies import get_current_admin


router = APIRouter()

@router.post("", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print('create_user')
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    print('read_users_me')
    return current_user


@router.get("", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    print('read_users')
    users = crud.get_users(db, skip=skip, limit=limit)
    print(users)
    return users


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print('login_for_access_token')
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

