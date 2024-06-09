import configparser
import pathlib
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import models as m #type: ignore

# URI: postgresql://username:password@domain.port/database

file_config = './myapp/config.ini'
config = configparser.ConfigParser()
config.read(file_config)

sections = config.sections()
print(f"Sections found: {sections}")



if 'DEV_DB' in sections:
    # Fetching configuration for the DEV_DB section
    user = config.get('DEV_DB', 'USER')
    password = config.get('DEV_DB', 'PASSWORD')
    domain = config.get('DEV_DB', 'DOMAIN')
    port = config.get('DEV_DB', 'PORT')
    db = config.get('DEV_DB', 'DB_NAME')

    # Construct the connection URI
    URI = f"postgresql+psycopg2://{user}:{password}@{domain}:{port}/{db}"
    #onnection_string = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'

    print(URI)
    # postgresql+psycopg2://marina_admin:mar123@@@@localhost:5432/homework_6
    # postgresql+psycopg2://marina_admin:mar123@localhost:5432/homework_6

    # Create the SQLAlchemy engine
    #engine = create_engine(URI, echo=False, pool_size=5, max_overflow=0)
    engine = create_engine(URI)
    #DBSession = sessionmaker(bind=engine)
    #session = DBSession()
    
    try:
        with engine.connect() as connection:
            print("Connection successful")
    
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    except Exception as e:
        print(f"Connection failed: {e}")

    #users = await session.execute(select(User))
    #columns = ["id", "fullname"]
    #result = [dict(zip(columns, (row.id, row.fullname))) for row in users.scalars()]
    #print(result)

    #result = session.execute(select(m.Student))
    #for el in result.scalars():
    #print(result)
    #print("Connected to database successfully.")
else:
    print("DEV_DB section not found in config file.")