try:
    from backend.app.database import Base
except ImportError:
    from database import Base

from sqlalchemy import Column, Integer, String, DateTime, func, Text
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
    business_url = Column(String)
    embed_code = Column(String)
    created_at = Column(DateTime, default=func.now())
    # Add customization settings
    font_family = Column(String)
    text_color = Column(String)
    star_color = Column(String)
    text_size = Column(String)
    container_width = Column(String)
    reviews_per_row = Column(Integer)

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String, index=True)  # Add this line
    author = Column(String, index=True)  # Author of the review
    rating = Column(String)  # Rating of the review
    content = Column(Text)  # Content of the review
    date = Column(DateTime, default=func.now())  # Date of the review
    user_id = Column(Integer, ForeignKey('users.id'))  # Link to the user
    profile_photo_url = Column(String, nullable=True)

    # Define the relationship with the user
    user = relationship("User", back_populates="reviews")

class BusinessSelection(Base):
    __tablename__ = "business_selections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # One business per user
    place_id = Column(String, nullable=False)
    business_name = Column(String, nullable=False)
    business_address = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Define the relationship with the user
    user = relationship("User", backref="business_selection")