import configparser
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database
from settings import settings

def create_postgres_database():
    if hasattr(settings, "postgres_user") and hasattr(settings, "postgres_password") and \
       hasattr(settings, "postgres_domain")  and hasattr(settings, "postgres_port") and \
       hasattr(settings, "postgres_db_name") :
    
        user = settings.postgres_user          
        password = settings.postgres_password  
        domain = settings.postgres_domain      
        port = settings.postgres_port          
        db = settings.postgres_db_name         
    
        # Construct the connection URI for the existing database to create the new one
        URI = f"postgresql+psycopg2://{user}:{password}@{domain}:{port}/postgres"
    
        try:
            # Create the SQLAlchemy engine for the default 'postgres' database
            engine = create_engine(URI)
    
            # Define the URL for the new database
            database_url = f"postgresql+psycopg2://{user}:{password}@{domain}:{port}/{db}"
    
            # Drop the database if it exists
            if database_exists(database_url):
                drop_database(database_url)
                #return f"Database {db} dropped successfully!"
    
            # Create the new database
            create_database(database_url)
            return f"Database {db} created successfully!"
    
        except Exception as e:
            return f"An error occurred: {e}"
    
    else:
        return "POSTGRES_DB section not found or missing in .env file."

