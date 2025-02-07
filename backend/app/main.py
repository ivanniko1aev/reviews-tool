from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
import asyncio
import secrets
from backend.app.database import get_db, engine, Base
from backend.app.models import User, EmbedSnippet
from backend.app.scraper import get_google_reviews

# Initialize FastAPI
app = FastAPI()

# Mount the frontend directory to serve static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Input structure for scraping requests
class ScrapeRequest(BaseModel):
    google_maps_url: str

# Input structure for user signup
class SignupRequest(BaseModel):
    email: str

@app.get("/", response_class=HTMLResponse)
async def home():
    """ Serve the frontend HTML page """
    with open("frontend/index.html") as f:
        return HTMLResponse(content=f.read())   

@app.post("/signup/")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """ Signup endpoint to generate API keys """
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        return {"message": "User already exists", "api_key": existing_user.api_key}

    api_key = secrets.token_hex(16)
    new_user = User(email=request.email, api_key=api_key)
    db.add(new_user)
    db.commit()
    return {"message": "User created", "api_key": api_key}

@app.post("/scrape-reviews/")
async def scrape_reviews(request: ScrapeRequest, api_key: str = Header(None), db: Session = Depends(get_db)):
    """ Scrape reviews (Protected with API Key) """
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        # Run the scraping tool in a separate thread
        loop = asyncio.get_event_loop()
        reviews = await loop.run_in_executor(None, get_google_reviews, request.google_maps_url)

        # Store in DB
        embed_code = f'<div class="reviews-widget">{reviews}</div>'
        new_snippet = EmbedSnippet(user_id=user.id, business_url=request.google_maps_url, embed_code=embed_code)
        db.add(new_snippet)
        db.commit()

        return {"reviews": reviews, "embed_code": embed_code}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-snippets/")
def get_snippets(api_key: str = Header(None), db: Session = Depends(get_db)):
    """ Fetch stored review snippets (Protected with API Key) """
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    snippets = db.query(EmbedSnippet).filter(EmbedSnippet.user_id == user.id).all()
    return {"snippets": [{"business_url": s.business_url, "embed_code": s.embed_code} for s in snippets]}
