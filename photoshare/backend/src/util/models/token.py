from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime
from .base import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    token = Column(String, primary_key=True, unique=True, index=True)
    blacklisted_on = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<BlacklistedToken(token={self.token}, blacklisted_on={self.blacklisted_on})>"
