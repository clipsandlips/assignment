import configparser
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

# Load configuration from config.ini file
file_config = 'db_psql_config.ini'
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
    print("DEV_DB section not found in config file.")

