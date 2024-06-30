import os
from itsdangerous import URLSafeTimedSerializer
import aiosmtplib 
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape
import configparser
from settings import settings

if hasattr(settings, "smtp_username") and hasattr(settings, "smtp_password") and \
   hasattr(settings, "smtp_hostname") :

    smtp_username = settings.smtp_username  
    smtp_password = settings.smtp_password
    smtp_hostname = settings.smtp_hostname

if hasattr(settings, "hash_secret_key") and hasattr(settings, "hash_salt") :
    
    SECRET_KEY = settings.hash_secret_key  
    SALT = settings.hash_salt


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
