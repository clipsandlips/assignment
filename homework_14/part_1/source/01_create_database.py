import configparser
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database
from settings import settings

# Load configuration from config.ini file
#file_config = '.env'
#config = configparser.ConfigParser()
#config.read(file_config)

#sections = config.sections()
#print(f"Sections found: {sections}")

#if 'POSTGRES_DB' in sections:


if hasattr(settings, "postgres_user") and hasattr(settings, "postgres_password") and \
   hasattr(settings, "postgres_domain")  and hasattr(settings, "postgres_port") and \
   hasattr(settings, "postgres_db_name") :
 
    user = settings.postgres_user           #config.get('POSTGRES_DB', 'USER')
    password = settings.postgres_password   #config.get('POSTGRES_DB', 'PASSWORD')
    domain = settings.postgres_domain       #config.get('POSTGRES_DB', 'DOMAIN')
    port = settings.postgres_port           #config.get('POSTGRES_DB', 'PORT')
    db = settings.postgres_db_name          #config.get('POSTGRES_DB', 'DB_NAME')

    # Construct the connection URI for the existing database to create the new one
    URI = f"postgresql+psycopg2://{user}:{password}@{domain}:{port}/postgres"
    print(URI)

    try:
        # Create the SQLAlchemy engine for the default 'postgres' database
        engine = create_engine(URI)

        # Define the URL for the new database
        database_url = f"postgresql+psycopg2://{user}:{password}@{domain}:{port}/{db}"
        print(database_url)

        # Drop the database if it exists
        if database_exists(database_url):
            drop_database(database_url)
            print(f"Database {db} dropped successfully!")

        # Create the new database
        create_database(database_url)
        print(f"Database {db} created successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

else:
    print("POSTGRES_DB section not found or missing in .env file.")

