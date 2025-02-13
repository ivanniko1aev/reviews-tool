from sqlalchemy import Column, Integer, String, DateTime, func, Text
from backend.app.database import Base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)  # Store Google profile picture
    created_at = Column(DateTime, default=func.now())
    
    # Define the relationship with the reviews
    reviews = relationship("Review", back_populates="user")


class EmbedSnippet(Base):
    __tablename__ = "embed_snippets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_url = Column(String, unique=True)
    embed_code = Column(String)
    created_at = Column(DateTime, default=func.now())

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String, index=True)  # Author of the review
    rating = Column(String)  # Rating of the review
    content = Column(Text)  # Content of the review
    date = Column(DateTime, default=func.now())  # Date of the review
    user_id = Column(Integer, ForeignKey('users.id'))  # Link to the user

    # Define the relationship with the user
    user = relationship("User", back_populates="reviews")