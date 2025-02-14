import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.routers import pages, auth, business, reviews, embed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "default_secret_key"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(pages.router, tags=["pages"])
app.include_router(auth.router, prefix="/api/authentication", tags=["auth"])
app.include_router(business.router, prefix="/api", tags=["business"])
app.include_router(reviews.router, prefix="/api", tags=["reviews"])
app.include_router(embed.router, prefix="/api", tags=["embed"])