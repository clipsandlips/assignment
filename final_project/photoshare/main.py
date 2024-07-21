import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from backend.src.routes import users, photos, tags

from fastapi import FastAPI
from photoshare.backend.src.util.database import engine
from photoshare.backend.src.util.models import models

import cloudinary
from backend.src.config.config import settings


cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET
)


#models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(photos.router)
app.include_router(tags.router)

@app.get("/")
async def root():
    return {"message": "Welcome to PhotoShare API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)