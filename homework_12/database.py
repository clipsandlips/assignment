from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import configparser
from sqlalchemy.orm import Session
import models


# Load configuration from config.ini
config = configparser.ConfigParser()
config.read("db_psql_config.ini")

DB_USER = config["DEV_DB"]["USER"]
DB_PASSWORD = config["DEV_DB"]["PASSWORD"]
DB_HOST = config["DEV_DB"]["DOMAIN"]
DB_PORT = config["DEV_DB"]["PORT"]
DB_NAME = config["DEV_DB"]["DB_NAME"]

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()