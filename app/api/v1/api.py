"""
Main router for API version 1.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, payments, policies, premiums

# Import routers for different resources here
# from .endpoints import items, ...

api_router = APIRouter()

# Include routers here
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(premiums.router, prefix="/premiums", tags=["premiums"])
# api_router.include_router(items.router, prefix="/items", tags=["items"]) 