from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from backend.app.scraper import get_google_reviews, save_reviews_to_csv
from pydantic import BaseModel
import asyncio

app = FastAPI()

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Define the input structure for the request
class ScrapeRequest(BaseModel):
    google_maps_url: str
    
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("frontend/index.html") as f:
        return HTMLResponse(content=f.read())   

# Route to handle the scraping logic
@app.post("/scrape-reviews")
async def scrape_reviews(request: ScrapeRequest):
    try:
        # Run the scraping tool in a separate thread (so it doesn't block FastAPI's event loop)
        loop = asyncio.get_event_loop()
        reviews = await loop.run_in_executor(None, get_google_reviews, request.google_maps_url)
        
        return {"reviews": reviews}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-reviews/{file_name}")
async def download_reviews(file_name: str):
    try:
        file_path = save_reviews_to_csv(file_name)
        return {"file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
