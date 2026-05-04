from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

class Binding(Base):
    __tablename__ = "bindings"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    proxy_id = Column(Integer, ForeignKey("proxies.id"), nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=True)

    account = relationship("Account")
    proxy = relationship("Proxy")
    profile = relationship("Profile")
