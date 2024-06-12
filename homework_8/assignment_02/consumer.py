import pika #type: ignore
import json
import time
import mongoengine as me  # type: ignore
from mongoengine import connect  # type: ignore

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

# Define the contact model
class Contact(me.Document):
    fullname = me.StringField(required=True, max_length=200)
    email = me.StringField(required=True, max_length=50)
    flag = me.BooleanField(required=True, default=False)
    comment = me.StringField(required=True, max_length=500)

# RabbitMQ setup
rabbitmq_secrets = read_secrets('rabbitmq_secrets.json')
rabbitmq_user = rabbitmq_secrets['username']
rabbitmq_password = rabbitmq_secrets['password']
rabbitmq_host = 'localhost' 
rabbitmq_queue = 'email_queue'

credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
parameters = pika.ConnectionParameters(
    host=rabbitmq_host,
    port=5672,  # default RabbitMQ port
    virtual_host='/',
    credentials=credentials
)

def callback(ch, method, properties, body):
    contact_data = json.loads(body)
    print(f"Sending email to {contact_data['fullname']} at {contact_data['email']}")
    time.sleep(1)  # Simulate the time taken to send an email
    print(f"Email sent to {contact_data['email']}")

    # Update the flag in MongoDB
    contact = Contact.objects(id=contact_data['id']).first()
    if contact:
        contact.flag = True
        contact.save()
        print(f"Updated flag for contact {contact_data['email']} in MongoDB")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=rabbitmq_queue, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback)
        print('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")

if __name__ == "__main__":
    start_consumer()
