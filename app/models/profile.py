from sqlalchemy import Column, Integer, String
from app.models.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    adspower_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    status = Column(String, default="stopped")
