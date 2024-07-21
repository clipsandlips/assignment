from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.src.util.schemas import schemas
from backend.src.util.models import models
from backend.src.util.crud import crud
from backend.src.config.auth import get_db, get_current_active_user
from backend.src.config.dependencies import get_current_moderator, get_current_admin
from typing import List
import cloudinary
import cloudinary.uploader
#import qrcode


router = APIRouter()

@router.post("/photos/", response_model=schemas.Photo)
async def create_photo(
    description: str,
    tags: List[str] = [],
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Upload photo to Cloudinary
    result = cloudinary.uploader.upload(file.file)
    url = result['secure_url']

    # Create photo in database
    photo = crud.create_photo(db, url, description, current_user.id, tags)
    return photo

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
    if db_photo.owner_id != current_user.id and current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_photo(db, db_photo, photo)

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
    crud.delete_photo(db, db_photo)

@router.post("/photos/{photo_id}/transform", response_model=schemas.TransformedImage)
async def transform_photo(
    photo_id: int,
    transformation: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    photo = crud.get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Apply Cloudinary transformation
    transformed_url = cloudinary.CloudinaryImage(photo.url).build_url(transformation=transformation)

    # Generate QR code
    #qr = qrcode.QRCode(version=1, box_size=10, border=5)
    #qr.add_data(transformed_url)
    #qr.make(fit=True)
    #qr_img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code to Cloudinary
    #buffer = io.BytesIO()
    #qr_img.save(buffer, format="PNG")
    #buffer.seek(0)
    #qr_result = cloudinary.uploader.upload(buffer)
    #qr_url = qr_result['secure_url']

    # Save transformed image info to database
    #transformed_image = crud.create_transformed_image(db, photo_id, transformed_url, qr_url)
    return '' # transformed_image

# Add more photo-related endpoints as needed