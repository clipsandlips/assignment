from fastapi import FastAPI, APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.schemas import photo as schema_photo, user as schema_user, tag as schema_tag
from backend.src.util.models import photo as model_photo, user as model_user
from backend.src.util.crud import photo as crud_photo
from backend.src.config.security import get_current_active_user
from backend.src.util.db import get_db
#from backend.src.config.dependencies import is_administrator, is_moderator
from backend.src.config.dependencies import role_required
from typing import List, Optional
import cloudinary
import cloudinary.uploader
from backend.src.util.logging_config import logger
#import qrcode
from sqlalchemy.future import select

router = APIRouter()

@router.post("/photos/", response_model=schema_photo.Photo)
async def create_photo(
    description: str = Form(None),
    tags: str = Form(""),
    file: UploadFile = File(...),
    current_user: schema_user.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Upload file to Cloudinary
    logger.debug('start : upload')
    upload_result = cloudinary.uploader.upload(file.file)
    logger.debug('end : upload')
    
    # Convert comma-separated tags into a list of TagCreate objects
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    tags_objects = [schema_tag.TagCreate(name=tag) for tag in tag_list]
    
    # Create PhotoCreate schema instance
    logger.debug('start : schema_photo')
    photo_in = schema_photo.PhotoCreate(
        url=upload_result["secure_url"], 
        description=description, 
        tags=tags_objects
    )
    logger.debug('end : schema_photo')
    
    # Use CRUD function to create photo in the database
    logger.debug('start : create_photo in database')
    return await crud_photo.create_photo(db=db, photo=photo_in, user_id=current_user.id)





@router.get("/photos/{photo_id}", response_model=schema_photo.Photo)
async def read_photo(photo_id: int, db: AsyncSession = Depends(get_db)):
    photo = await crud_photo.get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo



@router.put("/photos/{photo_id}", response_model=schema_photo.Photo)
@role_required("admin", "moderator")
async def update_photo(
    photo_id: int,
    photo: schema_photo.PhotoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model_user.User = Depends(get_current_active_user)
):
    db_photo = await crud_photo.get_photo(db, photo_id)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    if db_photo.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud_photo.update_photo(db, photo_id, photo)



@router.delete("/photos/{photo_id}", status_code=204)
@role_required("admin")
async def delete_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: model_user.User = Depends(get_current_active_user)
):
    db_photo = await crud_photo.get_photo(db, photo_id)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    if db_photo.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await crud_photo.delete_photo(db, photo_id)




@router.post("/photos/{photo_id}/transform", response_model=schema_photo.Photo)
@role_required("admin", "moderator")
async def transform_photo(
    photo_id: int,
    transformation: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(model_photo.Photo).filter(model_photo.Photo.id == photo_id))
    db_photo = result.scalars().first()
    if not db_photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        transformed_photo = await crud_photo.transform_photo(db, db_photo, transformation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return transformed_photo