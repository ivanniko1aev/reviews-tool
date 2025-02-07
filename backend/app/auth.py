from fastapi import HTTPException, Header, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

def get_current_user(api_key: str = Header(None), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return user
