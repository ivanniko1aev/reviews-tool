import asyncio
import secrets
import logging
import os
import requests
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, EmbedSnippet
from backend.app.auth import router as auth_router
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.app.scraper import GoogleReviewScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "default_secret_key"))
app.include_router(auth_router, prefix="/api/authentication", tags=["auth"])

# Allow CORS for your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Mount the new `static/` directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Configure Jinja templates (now in `templates/`)
templates = Jinja2Templates(directory="templates")

# Input structure for scraping requests
class ScrapeRequest(BaseModel):
    google_maps_url: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    logger.info("Handling request to home page")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scrape-reviews/")
async def scrape_reviews(request: ScrapeRequest, db: Session = Depends(get_db)):
    logger.info(f"Handling scrape reviews request for URL: {request.google_maps_url}")
    user_email = request.session.get("user_email")
    if not user_email:
        logger.warning("Unauthorized attempt to scrape reviews - no user email in session")
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        loop = asyncio.get_event_loop()
        logger.info("Starting review scraping process")
        reviews = await loop.run_in_executor(None, get_google_reviews, request.google_maps_url)
        embed_code = f'<div class="reviews-widget">{reviews}</div>'
        
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            logger.error(f"User not found in database: {user_email}")
            raise HTTPException(status_code=404, detail="User not found")
        
        new_snippet = EmbedSnippet(user_id=user.id, business_url=request.google_maps_url, embed_code=embed_code)
        db.add(new_snippet)
        db.commit()
        logger.info(f"Successfully saved new embed snippet for user: {user_email}")
        
        return {"reviews": reviews, "embed_code": embed_code}
    except Exception as e:
        logger.error(f"Error while scraping reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-snippets/")
def get_snippets(request: Request, db: Session = Depends(get_db)):
    logger.info("Handling get snippets request")
    user_email = request.session.get("user_email")
    if not user_email:
        logger.warning("Unauthorized attempt to get snippets - no user email in session")
        raise HTTPException(status_code=401, detail="User not authenticated")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        logger.error(f"User not found in database: {user_email}")
        raise HTTPException(status_code=404, detail="User not found")
        
    snippets = db.query(EmbedSnippet).filter(EmbedSnippet.user_id == user.id).all()
    logger.info(f"Retrieved {len(snippets)} snippets for user: {user_email}")
    return {"snippets": [{"business_url": s.business_url, "embed_code": s.embed_code} for s in snippets]}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    logger.info("Handling dashboard request")
    user_email = request.session.get("user_email")
    user_name = request.session.get("user_name")
    user_picture = request.session.get("user_picture")
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    google_maps_api_secret = os.getenv("GOOGLE_MAPS_API_SECRET")

    if not user_email:
        logger.warning("Unauthorized attempt to access dashboard - redirecting to login")
        return RedirectResponse(url="/login")

    logger.info(f"Rendering dashboard for user: {user_email}")
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_email": user_email,
        "user_name": user_name,
        "user_picture": user_picture,
        "google_maps_api_key": google_maps_api_key,
        "google_maps_api_secret": google_maps_api_secret
    })

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    logger.info("Handling login page request")
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/autocomplete/")
async def autocomplete(location: str = Form(...)):
    logger.info(f"Handling autocomplete request for location: {location}")
    api_key = os.getenv("GOOGLE_API_KEY")
    url = "https://places.googleapis.com/v1/places:autocomplete"

    payload = {
        "input": location,
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": 37.7937,
                    "longitude": -122.3965
                },
                "radius": 500.0
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key
    }

    response = requests.post(url, json=payload, headers=headers)
    suggestions = response.json().get('predictions', [])
    logger.info(f"Retrieved {len(suggestions)} autocomplete suggestions")
    return {"suggestions": suggestions}

# Proxy endpoint to Google Places API
@app.post("/api/places")
async def get_places(request: Request):
    data = await request.json()
    text_query = data.get("textQuery")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    url = "https://places.googleapis.com/v1/places:searchText"
    
    logger.info(f"Received text query: {text_query}")

    # Update the headers to request only the necessary fields
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName"  # Requesting only place_id and displayName
    }
    payload = {"textQuery": text_query}

    logger.info(f"Payload sent to Google Places API: {payload}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        api_response = response.json()  # Get the JSON response
        logger.info(f"Response from Google Places API: {api_response}")  # Log the response
        return api_response
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching places: {e}")
        raise HTTPException(status_code=500, detail="Error fetching places")

@app.get("/api/reviews/{place_id}")
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