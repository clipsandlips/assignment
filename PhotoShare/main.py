import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend', 'src')))


from backend.src.routes import users, photos, tags
from backend.src.config.config import settings
from fastapi import FastAPI

#from app.routers import users, photos, tags
from backend.src.util.database import engine
from backend.src.util.models import models
from sqlalchemy.exc import ProgrammingError

import cloudinary
from sqlalchemy import inspect

def create_tables_if_not_exist(engine):
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    for table in models.Base.metadata.sorted_tables:
        print(table)
        if table.name not in existing_tables:
            table.create(engine)




cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_API_SECRET
)

#models.Base.metadata.create_all(bind=engine)

#models.Base.metadata.drop_all(bind=engine)
#models.Base.metadata.create_all(bind=engine)

create_tables_if_not_exist(engine)

#try:
#    models.Base.metadata.create_all(bind=engine)
#except ProgrammingError as e:
#    if "already exists" not in str(e):
#        raise



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

#@app.on_event("startup")
#async def on_startup():
#    logger.info("Creating all tables if they do not exist...")
#    #models.Base.metadata.create_all(bind=engine)
#    logger.info("Table creation completed.")

app.include_router(users.router)
app.include_router(photos.router)
app.include_router(tags.router)

@app.get("/")
async def root():
    return {"message": "Welcome to PhotoShare API"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)