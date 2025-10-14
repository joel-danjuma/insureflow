"""
API router configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, users, brokers, policies, premiums, 
    payments, dashboard, notifications, reminders, virtual_accounts, insureflow_admin, settlements, testing
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(brokers.router, prefix="/brokers", tags=["brokers"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(premiums.router, prefix="/premiums", tags=["premiums"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(virtual_accounts.router, prefix="/virtual-accounts", tags=["virtual-accounts"])
api_router.include_router(insureflow_admin.router, prefix="/admin/insureflow", tags=["insureflow-admin"])
api_router.include_router(settlements.router, prefix="/settlements", tags=["settlements"])
api_router.include_router(testing.router, prefix="/testing", tags=["testing"]) 