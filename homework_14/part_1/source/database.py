from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import configparser
from sqlalchemy.orm import Session
import models

from settings import settings

Base = declarative_base()
 
if hasattr(settings, "postgres_user") and hasattr(settings, "postgres_password") and \
   hasattr(settings, "postgres_domain")  and hasattr(settings, "postgres_port") and \
   hasattr(settings, "postgres_db_name") :
 
    db_user = settings.postgres_user           
    db_password = settings.postgres_password   
    db_host = settings.postgres_domain       
    db_port = settings.postgres_port           
    db_name = settings.postgres_db_name        

    SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    #print(SQLALCHEMY_DATABASE_URL)

    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
    except Exception as e:
        print(f"An error occurred: {e}")

else:
    print(f"POSTGRES_DB sections  not found or missing in .env file.")



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()