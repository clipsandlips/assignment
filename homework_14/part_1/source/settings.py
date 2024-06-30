from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db_name: str
    postgres_domain: str
    postgres_port: str
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    smtp_username: str
    smtp_password: str
    smtp_hostname: str
    hash_secret_key: str
    hash_salt: str
    
    class Config:
        env_file = ".env"

settings = Settings()


