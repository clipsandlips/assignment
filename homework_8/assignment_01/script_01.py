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
    
# Read secrets from the secrets.json file
secrets = read_secrets('secrets.json')
username = secrets['username']
password = secrets['password']

connection_string = 'mongodb+srv://{}:{}@cluster0.pfry08b.mongodb.net/homework_8_01_mongo_db?retryWrites=true&w=majority'.format(username, password)
print(connection_string)
# Connect to MongoDB using the credentials from the secret file
connect(host=connection_string)


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
    with open(authors_file, 'r', encoding='utf-8') as f:
        authors_data = json.load(f)
        for author in authors_data:
            Author(
                fullname=author['fullname'],
                born_date=author['born_date'],
                born_location=author['born_location'],
                description=author['description']
            ).save()
    
    # Read and upload quotes
    with open(quotes_file, 'r', encoding='utf-8') as f:
        quotes_data = json.load(f)
        for quote in quotes_data:
            Quote(
                tags=quote['tags'],
                author=quote['author'],
                quote=quote['quote']
            ).save()

def search_quotes(search_term, search_attribute):
    quotes = []
    
    if search_attribute == 'name':
        quotes = Quote.objects(author__icontains=search_term)
    elif search_attribute == 'tag':
        quotes = Quote.objects(tags__icontains=search_term)
    elif search_attribute == 'tags':
        tags = search_term.split(',')
        quotes = Quote.objects(tags__in=tags)
    
    return quotes

def main():
    # Upload JSON data to MongoDB
    upload_json_data('authors.json', 'quotes.json')
    
    # Interactive search loop
    while True:
        user_input = input("Enter a search query (format: attribute:term) or 'exit' to quit: ")
        if user_input.lower() == 'exit':
            break
        
        search_attribute = None
        search_term = None

        search_attribute = user_input.split(':')[0]
        print(search_attribute)
        search_term = user_input.split(":")[1]
        print(search_term)
        
        if not search_attribute:
            print("Invalid input format. Please use a valid format.")
            continue
        
        # Search and print quotes
        results = search_quotes(search_term, search_attribute)
        if results:
            for quote in results:
                print(f"Name: {quote.author}\nQuote: {quote.quote}\nTags: {', '.join(quote.tags)}\n")
        else:
            print("No quotes found.")

if __name__ == "__main__":
    main()