import json
from pymongo import MongoClient

import json
import pymongo
import os
import shutil
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from scrapy.utils.project import get_project_settings

import mongoengine as me # type: ignore

from mongoengine import Document, StringField, ListField, connect # type: ignore
from mongoengine.queryset.visitor import Q #type: ignore
import json

# Function to read secrets from a file
def read_secrets(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    

def export_collection_to_json(uri, db_name, collection_name, output_file):
    # Connect to MongoDB Atlas
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    # Fetch all documents from the collection
    documents = collection.find()

    # Convert documents to a list of dictionaries
    docs_list = [doc for doc in documents]

    # Remove '_id' field if necessary
    for doc in docs_list:
        if '_id' in doc:
            del doc['_id']

    # Write the list of dictionaries to a JSON file
    with open(output_file, 'w') as file:
        json.dump(docs_list, file, indent=4)

    print(f"Exported {len(docs_list)} documents from {db_name}.{collection_name} to {output_file}")


# Read secrets from the secrets.json file
secrets = read_secrets('db_mongo_secrets.json')
username = secrets['username']
password = secrets['password']
mongo_database = 'homework_9_01_mongo_db'

connection_string = 'mongodb+srv://{}:{}@cluster0.pfry08b.mongodb.net/{}?retryWrites=true&w=majority'.format(username, password, mongo_database)

print(connection_string)
connect(host=connection_string)

# Example usage
export_collection_to_json(connection_string, mongo_database, 'author', '_authors.json')
export_collection_to_json(connection_string, mongo_database, 'quote', '_quotes.json')