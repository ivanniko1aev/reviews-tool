from fastapi import APIRouter, Request, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import requests
import os
import logging
from ..database import get_db
from ..models import User, BusinessSelection

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/places")
async def get_places(request: Request):
    data = await request.json()
    text_query = data.get("textQuery")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress"
    }
    payload = {"textQuery": text_query}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching places: {e}")
        raise HTTPException(status_code=500, detail="Error fetching places")

@router.post("/save-business")
async def save_business(request: Request, db: Session = Depends(get_db)):
    user_email = request.session.get("user_email")
    if not user_email:
        raise HTTPException(status_code=401, detail="User not authenticated")

    data = await request.json()
    place_id = data.get("place_id")
    business_name = data.get("business_name")
    business_address = data.get("business_address")

    if not all([place_id, business_name]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        business_selection = db.query(BusinessSelection).filter(
            BusinessSelection.user_id == user.id
        ).first()

        if business_selection:
            business_selection.place_id = place_id
            business_selection.business_name = business_name
            business_selection.business_address = business_address
        else:
            business_selection = BusinessSelection(
                user_id=user.id,
                place_id=place_id,
                business_name=business_name,
                business_address=business_address
            )
            db.add(business_selection)

        db.commit()
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error saving business selection: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autocomplete/")
async def autocomplete(location: str = Form(...)):
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
    return {"suggestions": response.json().get('predictions', [])}

