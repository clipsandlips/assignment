import configparser
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('db_psql_config.ini')

user = config['DEV_DB']['USER']
password = config['DEV_DB']['PASSWORD']
host = config['DEV_DB']['DOMAIN']
port = config['DEV_DB']['PORT']
database = config['DEV_DB']['DB_NAME']

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = MetaData()