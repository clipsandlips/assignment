# database_operations.py

import configparser
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect
from datetime import datetime
import json

from settings import settings

if hasattr(settings, "postgres_user") and hasattr(settings, "postgres_password") and \
   hasattr(settings, "postgres_domain")  and hasattr(settings, "postgres_port") and \
   hasattr(settings, "postgres_db_name") :
 
    db_user = settings.postgres_user           
    db_password = settings.postgres_password   
    db_host = settings.postgres_domain       
    db_port = settings.postgres_port           
    db_name = settings.postgres_db_name     

    # Define the URL for the new database
    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    print(database_url)

    try:
        # Create the SQLAlchemy engine for the newly created database
        engine = create_engine(database_url)

        # Define a base class for declarative class definitions
        Base = declarative_base()

        # Define your models here
        class Author(Base):
            __tablename__ = 'quotes_author'

            id = Column(Integer, primary_key=True)
            fullname = Column(String(255), nullable=False)
            born_date = Column(Date, nullable=True)
            born_location = Column(String(255), nullable=True)
            description = Column(Text, nullable=True)

        class Quote(Base):
            __tablename__ = 'quotes_quote'

            id = Column(Integer, primary_key=True)
            text = Column(Text, nullable=False)
            author_id = Column(Integer, ForeignKey('quotes_author.id'), nullable=False)
            tags = Column(String(255), nullable=True)
            author = relationship('Author')

        # Create tables in the database if they do not exist
        inspector = inspect(engine)
        if not inspector.has_table('quotes_author'):
            Base.metadata.tables['quotes_author'].create(engine)
            print("Table 'quotes_author' created successfully!")
        else:
            print("Table 'quotes_author' already exists.")

        if not inspector.has_table('quotes_quote'):
            Base.metadata.tables['quotes_quote'].create(engine)
            print("Table 'quotes_quote' created successfully!")
        else:
            print("Table 'quotes_quote' already exists.")

        # Reconnect to the newly created database
        Session = sessionmaker(bind=engine)
        session = Session()

        # Load and insert authors data
        with open('_authors.json', 'r') as file:
            authors_data = json.load(file)
            for author_data in authors_data:
                born_date = datetime.strptime(author_data['born_date'], "%B %d, %Y").date() if author_data['born_date'] else None
                author = Author(
                    fullname=author_data['fullname'],
                    born_date=born_date,
                    born_location=author_data['born_location'],
                    description=author_data['description']
                )
                session.add(author)

        # Commit the authors to the database
        session.commit()

        # Load and insert quotes data
        with open('_quotes.json', 'r') as file:
            quotes_data = json.load(file)
            for quote_data in quotes_data:
                # Find the author in the database
                author = session.query(Author).filter_by(fullname=quote_data['author']).first()
                if author:
                    quote = Quote(
                        text=quote_data['quote'],
                        author_id=author.id,
                        tags=", ".join(quote_data['tags'])
                    )
                    session.add(quote)

        # Commit the quotes to the database
        session.commit()

        # Close the session
        session.close()

        print("Data imported successfully!")
    except IntegrityError as e:
        session.rollback()
        print(f"Integrity error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

else:
    print("DEV_DB section not found in config file.")
