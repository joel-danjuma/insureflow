"""
Main entry point for the InsureFlow application.
"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title="InsureFlow API",
    description="API for managing insurance policies, payments, and brokers.",
    version="0.1.0",
    openapi_url=f"/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# Set all CORS enabled origins
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    """
    Root endpoint for the application.
    """
    return {"message": "Welcome to InsureFlow API"} 