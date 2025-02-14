from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import logging
from backend.app.database import get_db
from backend.app.models import User, BusinessSelection

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    logger.info("Handling request to home page")
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    logger.info("Handling login page request")
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    logger.info("Handling dashboard request")
    user_email = request.session.get("user_email")
    user_name = request.session.get("user_name")
    user_picture = request.session.get("user_picture")
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    google_maps_api_secret = os.getenv("GOOGLE_MAPS_API_SECRET")

    if not user_email:
        logger.warning("Unauthorized attempt to access dashboard - redirecting to login")
        return RedirectResponse(url="/login")

    # Get user's saved business if it exists
    saved_business = None
    try:
        user = db.query(User).filter(User.email == user_email).first()
        if user:
            business_selection = db.query(BusinessSelection).filter(
                BusinessSelection.user_id == user.id
            ).first()
            if business_selection:
                saved_business = {
                    "place_id": business_selection.place_id,
                    "business_name": business_selection.business_name,
                    "business_address": business_selection.business_address
                }
                logger.info(f"Found saved business for user {user_email}: {business_selection.business_name}")
    except Exception as e:
        logger.error(f"Error fetching saved business: {e}")

    logger.info(f"Rendering dashboard for user: {user_email}")
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_email": user_email,
        "user_name": user_name,
        "user_picture": user_picture,
        "google_maps_api_key": google_maps_api_key,
        "google_maps_api_secret": google_maps_api_secret,
        "saved_business": saved_business  # Add saved business to template context
    })
