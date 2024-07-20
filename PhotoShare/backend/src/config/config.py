#from pydantic import BaseSettings
#from dotenv import load_dotenv
#from pydantic_settings import BaseSettings, SettingsConfigDict
#import os, sys

# Determine the path to the outer directory
#outer_package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#outer_package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#print(outer_package_path)

# Add the outer directory to the sys.path
#if outer_package_path not in sys.path:
#    sys.path.append(outer_package_path)

#from setting import setting


#load_dotenv()

from pydantic_settings import BaseSettings, SettingsConfigDict
import os


print('test')
print(os.path.join(os.path.dirname(__file__)))
          
class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_DB_NAME: str
    DATABASE_DOMAIN: str
    DATABASE_PORT: int

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_API_URL: str

    DEBUG: bool

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), '.env'))


    #model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

print("Loaded settings:", settings.model_dump())  # This will print all settings




