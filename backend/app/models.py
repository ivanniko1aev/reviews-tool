from sqlalchemy import Column, Integer, String, DateTime, func
from backend.app.database import Base
from sqlalchemy.sql.schema import ForeignKey

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)  # Store Google profile picture
    created_at = Column(DateTime, default=func.now())


class EmbedSnippet(Base):
    __tablename__ = "embed_snippets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_url = Column(String, unique=True)
    embed_code = Column(String)
    created_at = Column(DateTime, default=func.now())
