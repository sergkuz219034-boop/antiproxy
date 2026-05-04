from sqlalchemy import Column, Integer, String
from app.models.database import Base

class Proxy(Base):
    __tablename__ = "proxies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    host = Column(String)
    port = Column(Integer)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    protocol = Column(String, default="socks5")
