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
