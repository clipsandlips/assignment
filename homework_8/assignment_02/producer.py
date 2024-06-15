import mongoengine as me  # type: ignore
from mongoengine import Document, StringField, BooleanField, connect  # type: ignore
from faker import Faker
import json
import pika # type: ignore
import time

# Function to read secrets from a file
def read_secrets(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
 
# Read secrets from the secrets.json file
secrets = read_secrets('secrets.json')
username = secrets['username']
password = secrets['password']

connection_string = 'mongodb+srv://{}:{}@cluster0.pfry08b.mongodb.net/homework_8_02_mongo_db?retryWrites=true&w=majority'.format(username, password)
print(connection_string)
# Connect to MongoDB using the credentials from the secret file
connect(host=connection_string)

# RabbitMQ setup
rabbitmq_secrets = read_secrets('rabbitmq_secrets.json')
rabbitmq_user = rabbitmq_secrets['username']
rabbitmq_password = rabbitmq_secrets['password']
rabbitmq_host = 'localhost'
rabbitmq_queue = 'email_queue'

credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
parameters = pika.ConnectionParameters(rabbitmq_host, 5672, '/', credentials)
print(parameters)
connection = pika.BlockingConnection(parameters)
print(connection)
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_queue, durable=True)

# Define the contact model
class Contact(Document):
    fullname = StringField(required=True, max_length=200)
    email = StringField(required=True, max_length=50)
    flag = BooleanField(required=True, default=False)
    comment = StringField(required=True, max_length=500)




# Initialize Faker
fake = Faker()

def main():
    # Establish RabbitMQ connection
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=rabbitmq_queue, durable=True)
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return

    # Generate and save 100 fake contacts and send them to RabbitMQ
    for _ in range(100):
        contact = Contact(
            fullname=fake.name(),
            email=fake.email(),
            flag=False, #fake.boolean(),
            comment=fake.text(max_nb_chars=200)
        )
        contact.save()
        contact_data = {
            'id': str(contact.id),
            'fullname': contact.fullname,
            'email': contact.email,
            'flag': contact.flag,
            'comment': contact.comment
        }
        channel.basic_publish(
            exchange='',
            routing_key=rabbitmq_queue,
            body=json.dumps(contact_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        print(f"Sent {contact_data['email']} to the queue")

    connection.close()
    print("100 fake contacts have been created, saved to the database, and sent to the RabbitMQ queue.")

if __name__ == "__main__":
    main()



