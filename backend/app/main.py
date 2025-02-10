import asyncio
import secrets
import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db, engine, Base
from backend.app.models import User, EmbedSnippet
from backend.app.scraper import get_google_reviews
from backend.app.auth import router as auth_router
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "default_secret_key"))
app.include_router(auth_router, prefix="/api/authentication", tags=["auth"])

# ✅ Mount the new `static/` directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Configure Jinja templates (now in `templates/`)
templates = Jinja2Templates(directory="templates")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Input structure for scraping requests
class ScrapeRequest(BaseModel):
    google_maps_url: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scrape-reviews/")
async def scrape_reviews(request: ScrapeRequest, db: Session = Depends(get_db)):
    user_email = request.session.get("user_email")
    if not user_email:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        loop = asyncio.get_event_loop()
        reviews = await loop.run_in_executor(None, get_google_reviews, request.google_maps_url)
        embed_code = f'<div class="reviews-widget">{reviews}</div>'
        
        user = db.query(User).filter(User.email == user_email).first()
        new_snippet = EmbedSnippet(user_id=user.id, business_url=request.google_maps_url, embed_code=embed_code)
        db.add(new_snippet)
        db.commit()
        
        return {"reviews": reviews, "embed_code": embed_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-snippets/")
def get_snippets(request: Request, db: Session = Depends(get_db)):
    user_email = request.session.get("user_email")
    if not user_email:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user = db.query(User).filter(User.email == user_email).first()
    snippets = db.query(EmbedSnippet).filter(EmbedSnippet.user_id == user.id).all()
    return {"snippets": [{"business_url": s.business_url, "embed_code": s.embed_code} for s in snippets]}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user_email = request.session.get("user_email")
    user_name = request.session.get("user_name")
    user_picture = request.session.get("user_picture")

    if not user_email:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_email": user_email,
        "user_name": user_name,
        "user_picture": user_picture
    })

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
