from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.src.config.config import settings

#SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

#engine = create_engine(SQLALCHEMY_DATABASE_URL)
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base = declarative_base()



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.config.config import settings
from backend.src.util.models.models import Base  # Import Base from models.py

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# We no longer need to declare Base here, as it's imported from models.py

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()