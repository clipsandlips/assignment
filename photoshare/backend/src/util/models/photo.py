from fastapi import FastAPI, APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.src.util.schemas import schemas
from backend.src.util.models import models
from backend.src.util.crud import crud
from backend.src.config.auth import get_db, get_current_active_user
from backend.src.config.dependencies import get_current_moderator, get_current_admin
from typing import List, Optional
import cloudinary
import cloudinary.uploader

#import qrcode


router = APIRouter()

@router.post("/photos/", response_model=schemas.Photo)
async def create_photo(
    description: str = Form(None),
    tags: str = Form(""),
    file: UploadFile = File(...),
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Upload file to Cloudinary
    upload_result = cloudinary.uploader.upload(file.file)
    
    # Convert comma-separated tags into a list of TagCreate objects
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    tags_objects = [schemas.TagCreate(name=tag) for tag in tag_list]
    
    # Create PhotoCreate schema instance
    photo_in = schemas.PhotoCreate(
        url=upload_result["secure_url"], 
        description=description, 
        tags=tags_objects
    )
    
    # Use CRUD function to create photo in the database
    return crud.create_photo(db=db, photo=photo_in, user_id=current_user.id)


@router.get("/photos/{photo_id}", response_model=schemas.Photo)
def read_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = crud.get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.put("/photos/{photo_id}", response_model=schemas.Photo)
def update_photo(
    photo_id: int,
    photo: schemas.PhotoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_photo = crud.get_photo(db, photo_id)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    if db_photo.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_photo(db, photo_id, photo)

@router.delete("/photos/{photo_id}", status_code=204)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_photo = crud.get_photo(db, photo_id)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    if db_photo.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud.delete_photo(db, photo_id)

@router.post("/photos/{photo_id}/transform", response_model=schemas.Photo)
def transform_photo(
    photo_id: int,
    transformation: str,
    db: Session = Depends(get_db)
):
    db_photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if not db_photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        transformed_photo = crud.transform_photo(db, db_photo, transformation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return transformed_photo