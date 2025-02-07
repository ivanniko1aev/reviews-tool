from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())

class EmbedSnippet(Base):
    __tablename__ = "embed_snippets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_url = Column(String, unique=True)
    embed_code = Column(String)
    created_at = Column(DateTime, default=func.now())
