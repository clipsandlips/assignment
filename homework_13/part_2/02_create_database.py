import configparser
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from settings import settings

# Load configuration from config.ini file
#file_config = 'db_psql_config.ini'
#config = configparser.ConfigParser()
#config.read(file_config)

#sections = config.sections()
#print(f"Sections found: {sections}")




if hasattr(settings, "postgres_user") and hasattr(settings, "postgres_password") and \
   hasattr(settings, "postgres_domain")  and hasattr(settings, "postgres_port") and \
   hasattr(settings, "postgres_db_name") :
 
    db_user = settings.postgres_user           
    db_password = settings.postgres_password   
    db_host = settings.postgres_domain       
    db_port = settings.postgres_port           
    db_name = settings.postgres_db_name        

    # Construct the connection URI for the existing database to create the new one
    URI = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
    print(URI)

    try:
        # Create the SQLAlchemy engine for the default 'postgres' database
        engine = create_engine(URI)

        # Define the URL for the new database
        database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print(database_url)

        # Drop the database if it exists
        if database_exists(database_url):
            drop_database(database_url)
            print(f"Database {db_name} dropped successfully!")

        # Create the new database
        create_database(database_url)
        print(f"Database {db_name} created successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

else:
    print("DEV_DB section not found in config file.")

