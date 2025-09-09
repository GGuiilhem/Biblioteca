from fastapi import APIRouter
from app.api.endpoints import authors

api_router = APIRouter()
api_router.include_router(authors.router, prefix="/api", tags=["authors"])
