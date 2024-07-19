import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from app.routers import users, photos, tags

from fastapi import FastAPI
#from app.routers import users, photos, tags
from app.database import engine
from app import models

import cloudinary
from app.config import settings


cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(photos.router)
app.include_router(tags.router)

@app.get("/")
async def root():
    return {"message": "Welcome to PhotoShare API"}