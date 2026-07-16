from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    comment = Column(Text, nullable=False)
    ai_result = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)