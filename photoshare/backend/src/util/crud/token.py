from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models.token import BlacklistedToken
import time
from sqlalchemy.orm import Session
from src.util.db import SessionLocal
#from crud.token import remove_expired_tokens


def add_token_to_blacklist(db: Session, token: str):
    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()
    db.refresh(blacklisted_token)
    return blacklisted_token

def is_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None

def remove_expired_tokens(db: Session):
    expiration_time = datetime.utcnow() - timedelta(days=30)  # Set your TTL here
    db.query(BlacklistedToken).filter(BlacklistedToken.blacklisted_on < expiration_time).delete()
    db.commit()

def cleanup_expired_tokens():
    while True:
        db: Session = SessionLocal()
        try:
            remove_expired_tokens(db)
        finally:
            db.close()
        time.sleep(86400)  # Run once a day