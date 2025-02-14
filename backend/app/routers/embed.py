from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from ..database import get_db
from ..models import User, EmbedSnippet

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/save-embed")
async def save_embed(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        user_email = request.session.get("user_email")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        embed_snippet = db.query(EmbedSnippet).filter(
            EmbedSnippet.user_id == user.id
        ).first()

        if not embed_snippet:
            embed_snippet = EmbedSnippet(user_id=user.id)
            db.add(embed_snippet)

        embed_snippet.font_family = data.get('fontFamily')
        embed_snippet.text_color = data.get('textColor')
        embed_snippet.star_color = data.get('starColor')
        embed_snippet.text_size = data.get('textSize')
        embed_snippet.container_width = data.get('containerWidth')
        embed_snippet.reviews_per_row = data.get('reviewsPerRow')
        embed_snippet.embed_code = data.get('embedCode')
        embed_snippet.business_url = data.get('businessUrl')

        db.commit()
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error saving embed settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-snippets/")
def get_snippets(request: Request, db: Session = Depends(get_db)):
    logger.info("Handling get snippets request")
    user_email = request.session.get("user_email")
    if not user_email:
        raise HTTPException(status_code=401, detail="User not authenticated")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    snippets = db.query(EmbedSnippet).filter(EmbedSnippet.user_id == user.id).all()
    return {"snippets": [{"business_url": s.business_url, "embed_code": s.embed_code} for s in snippets]}

