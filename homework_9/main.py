import json
import pymongo
import os
import shutil
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from scrapy.utils.project import get_project_settings
from quotes_scraper.quotes_scraper.spiders.authors_spider import AuthorsSpider #type: ignore
from quotes_scraper.quotes_scraper.spiders.quotes_spider import QuotesSpider   #type: ignore


import mongoengine as me # type: ignore

from mongoengine import Document, StringField, ListField, connect # type: ignore
from mongoengine.queryset.visitor import Q #type: ignore
import json

import re
from functools import reduce

# Function to read secrets from a file
def read_secrets(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    


# Define the Author document model
class Author(Document):
    fullname = StringField(required=True, max_length=200)
    born_date = StringField(required=True, max_length=50)
    born_location = StringField(required=True, max_length=200)
    description = StringField(required=True)

# Define the Quote document model
class Quote(Document):
    tags = ListField(StringField(max_length=50))
    author = StringField(required=True, max_length=100)
    quote = StringField(required=True)

def upload_json_data(authors_file, quotes_file):
    # Read and upload authors
    try:
        with open(authors_file, 'r', encoding='utf-8') as f:
            try:
                authors_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding authors.json : {e}")
                return

            for author in authors_data:
                Author(
                    fullname=author['fullname'],
                    born_date=author['born_date'],
                    born_location=author['born_location'],
                    description=author['description']
                ).save()

        print('authors.json file uploaded.')

        # Read and upload quotes
        with open(quotes_file, 'r', encoding='utf-8') as f:
            try:
                quotes_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding quotes.json: {e}")
                return
            
            for quote in quotes_data:
                Quote(
                    tags=quote['tags'],
                    author=quote['author'],
                    quote=quote['quote']
                ).save()
        print('quotes.json file uploaded.')
    
    except Exception as e:
        print(f"Error uploading JSON data: {e}")
        raise



def run_spiders():
    settings_authors = get_project_settings()
    settings_authors.update({
        'FEEDS': {
            'output/authors.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 4,
            },
        },
        'LOG_LEVEL': 'DEBUG',  # Set log level to DEBUG to capture more details
    })

    settings_quotes = get_project_settings()
    settings_quotes.update({
        'FEEDS': {
            'output/quotes.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 4,
            },
        },
        'LOG_LEVEL': 'DEBUG',  # Set log level to DEBUG to capture more details
    })


    output_dir = 'output'

    # Check if the directory exists and delete it with all contents if it does
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
            print(f"Deleted {output_dir} directory and all its contents.")
        except Exception as e:
            print(f"Failed to delete {output_dir} directory. Reason: {e}")

    # Create the output directory
    os.makedirs(output_dir)



    process_authors = CrawlerProcess(settings_authors)
    process_authors.crawl(AuthorsSpider)

    process_quotes = CrawlerProcess(settings_quotes)
    process_quotes.crawl(QuotesSpider)

    process_authors.start()
    process_quotes.start()

    process_authors.join()
    process_quotes.join()

    print('Spiders have finished running.')

def main():
    # Run the spiders and save the output to JSON files
    #run_spider_for_authors()
    #run_spider_for_quotes()
    run_spiders()
    print('Spiders have finished running.')
    




    # Read secrets from the secrets.json file
    secrets = read_secrets('secrets.json')
    username = secrets['username']
    password = secrets['password']
    mongo_database = 'homework_9_01_mongo_db'

    connection_string = 'mongodb+srv://{}:{}@cluster0.pfry08b.mongodb.net/{}?retryWrites=true&w=majority'.format(username, password, mongo_database)

    print(connection_string)
    connect(host=connection_string)

    # Upload the saved JSON files to MongoDB
    authors_file='output/authors.json'
    quotes_file='output/quotes.json'
    upload_json_data(authors_file, quotes_file)
    print('Json files uploaded to mongodb.')

if __name__ == "__main__":
    main()









