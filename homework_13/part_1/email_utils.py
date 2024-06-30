import os
from itsdangerous import URLSafeTimedSerializer
import aiosmtplib 
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape
import configparser


# Load configuration from config.ini file
file_config = 'secrets.ini'
config = configparser.ConfigParser()
config.read(file_config)

sections = config.sections()
print(f"Sections found: {sections}")

if 'SMTP' in sections:
    smtp_username = config.get('SMTP', 'SMTP_USERNAME') 
    smtp_password = config.get('SMTP', 'SMTP_PASSWORD')
    smtp_hostname = config.get('SMTP', 'SMTP_HOSTNAME')
    
if 'HASH' in sections:
    SECRET_KEY = config.get('HASH', 'HASH_SECRET_KEY')  
    SALT = config.get('HASH', 'HASH_SALT')


def generate_confirmation_token(email: str):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SALT)

def confirm_token(token: str, expiration: int = 3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt=SALT, max_age=expiration)
    except Exception:
        return False
    return email

async def send_email(subject: str, recipient: str, html_content: str):
    message = EmailMessage()
    message["From"] = smtp_username
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname= smtp_hostname,
        port=587,
        start_tls=True,
        username=smtp_username,
        password=smtp_password,
    )



env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(['html', 'xml']))
template = env.get_template("email_verification.html")

async def send_verification_email(email: str, token: str):
    verification_url = f"http://127.0.0.1:8000/verify-email?token={token}"
    html_content = template.render(verification_url=verification_url)
    await send_email("Email Verification", email, html_content)
