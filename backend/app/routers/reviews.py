from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import asyncio
import logging
from backend.app.database import get_db
from backend.app.models import User, EmbedSnippet
from backend.app.scraper import GoogleReviewScraper

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
async def get_reviews(place_id: str):
    try:
        logger.info(f"Fetching reviews for place_id: {place_id}")
        scraper = GoogleReviewScraper()
        # Use the _fetch_reviews_api method directly since we already have the place_id
        reviews = scraper._fetch_reviews_api(place_id, max_reviews=5)
        
        if not reviews:
            logger.warning(f"No reviews found for place_id: {place_id}")
            return {"reviews": []}
            
        # Format the reviews
        formatted_reviews = []
        for review in reviews:
            formatted_reviews.append({
                'author': review.get('author_name', 'Anonymous'),
                'rating': review.get('rating', 0),
                'content': review.get('text', 'No content'),
                'time': review.get('time', None),
                'relative_time': review.get('relative_time_description', 'Recently'),
                'profile_photo_url': review.get('profile_photo_url', None)
            })
            
        logger.info(f"Successfully retrieved {len(formatted_reviews)} reviews")
        return {"reviews": formatted_reviews}
        
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))