import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / '.env'

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError(f"Could not find SQLALCHEMY_DATABASE_URL in {env_path}. Please check if the file exists and contains the correct variable.")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def save_reviews_to_db(db: Session, user_id: int, reviews: list):
    from app.models import Review
    for review in reviews:
        db_review = Review(
            author=review['author'],
            rating=review['rating'],
            content=review['content'],
            user_id=user_id
        )
        db.add(db_review)
    db.commit()