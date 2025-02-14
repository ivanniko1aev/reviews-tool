from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import asyncio
import logging
from backend.app.database import get_db
from backend.app.models import User, EmbedSnippet, Review
from backend.app.scraper import GoogleReviewScraper
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Move the request model here
class ScrapeRequest(BaseModel):
    google_maps_url: str

@router.post("/scrape-reviews/")
async def scrape_reviews(request: ScrapeRequest, db: Session = Depends(get_db)):
    logger.info(f"Handling scrape reviews request for URL: {request.google_maps_url}")
    user_email = request.session.get("user_email")
    if not user_email:
        logger.warning("Unauthorized attempt to scrape reviews - no user email in session")
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        scraper = GoogleReviewScraper()
        loop = asyncio.get_event_loop()
        logger.info("Starting review scraping process")
        reviews = await loop.run_in_executor(None, scraper.get_google_reviews, request.google_maps_url)
        embed_code = f'<div class="reviews-widget">{reviews}</div>'
        
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            logger.error(f"User not found in database: {user_email}")
            raise HTTPException(status_code=404, detail="User not found")
        
        new_snippet = EmbedSnippet(
            user_id=user.id, 
            business_url=request.google_maps_url, 
            embed_code=embed_code
        )
        db.add(new_snippet)
        db.commit()
        logger.info(f"Successfully saved new embed snippet for user: {user_email}")
        
        return {"reviews": reviews, "embed_code": embed_code}
    except Exception as e:
        logger.error(f"Error while scraping reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{place_id}")
async def get_reviews(
    place_id: str, 
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Fetching reviews for place_id: {place_id}")
        
        user_email = request.session.get("user_email")
        if not user_email:
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check for existing reviews
        existing_reviews = db.query(Review).filter(Review.place_id == place_id).all()
        
        if existing_reviews:
            logger.info(f"Found {len(existing_reviews)} existing reviews in database")
            formatted_reviews = [{
                'author': review.author,
                'rating': review.rating,
                'content': review.content,
                'time': review.date.timestamp() if review.date else None,
                'relative_time': "Previously saved",
                'profile_photo_url': review.profile_photo_url
            } for review in existing_reviews]
            
            return {"reviews": formatted_reviews}
            
        # Fetch new reviews from API
        logger.info("No existing reviews found, fetching from API")
        scraper = GoogleReviewScraper()
        reviews = scraper._fetch_reviews_api(place_id, max_reviews=5)
        
        if not reviews:
            logger.warning(f"No reviews found for place_id: {place_id}")
            return {"reviews": []}
            
        # Save reviews to database
        for review_data in reviews:
            new_review = Review(
                place_id=place_id,
                author=review_data.get('author_name', 'Anonymous'),
                rating=str(review_data.get('rating', 0)),
                content=review_data.get('text', 'No content'),
                date=datetime.fromtimestamp(review_data.get('time')) if review_data.get('time') else None,
                user_id=user.id,
                profile_photo_url=review_data.get('profile_photo_url')
            )
            db.add(new_review)
        
        db.commit()
        logger.info(f"Saved {len(reviews)} new reviews to database")
            
        # Format the reviews for response
        formatted_reviews = [{
            'author': review.get('author_name', 'Anonymous'),
            'rating': review.get('rating', 0),
            'content': review.get('text', 'No content'),
            'time': review.get('time', None),
            'relative_time': review.get('relative_time_description', 'Recently'),
            'profile_photo_url': review.get('profile_photo_url')
        } for review in reviews]
            
        return {"reviews": formatted_reviews}
        
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))