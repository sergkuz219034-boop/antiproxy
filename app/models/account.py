from sqlalchemy import Column, Integer, String
from app.models.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    cookies = Column(String, nullable=True)
    status = Column(String, default="active")
