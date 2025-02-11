import os
import logging
import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid email profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )

    return RedirectResponse(url=google_auth_url)

@router.get("/callback")
async def auth_callback(request: Request, code: str, db: Session = Depends(get_db)):
    token_request_uri = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': request.url_for('auth_callback'),
        'grant_type': 'authorization_code',
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_request_uri, data=data)
            # Log the response status and body for debugging
            logger.debug(f"Response from Google: {response.status_code}")
            logger.debug(f"Response body: {response.text}")
            
            response.raise_for_status()  # This will raise an error if the response code is not 200
            token_response = response.json()

        id_token_value = token_response.get('id_token')
        if not id_token_value:
            raise HTTPException(status_code=400, detail="Missing id_token in response.")

        try:
            id_info = id_token.verify_oauth2_token(id_token_value, google_requests.Request(), GOOGLE_CLIENT_ID)

            email = id_info.get('email')
            name = id_info.get('name')
            picture = id_info.get('picture')

            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(email=email, name=name, picture=picture)
                db.add(user)
                db.commit()

            # Store session
            request.session['user_email'] = email
            request.session['user_name'] = name
            request.session['user_picture'] = picture

            logger.info(f"User {email} authenticated successfully.")

            return RedirectResponse(url="/dashboard")  # Redirect user to dashboard

        except ValueError as e:
            logger.error(f"Error verifying id_token: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid id_token: {str(e)}")

    except httpx.RequestError as e:
        logger.error(f"RequestError during token exchange: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during token exchange.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")
