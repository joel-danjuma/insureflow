"""
API endpoints for settlement management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_admin_user, get_current_insurance_user
from app.models.user import User
from app.services.settlement_service import settlement_service
from app.schemas.settlement import SettlementResponse

router = APIRouter()


@router.post("/process-daily", status_code=status.HTTP_200_OK)
async def process_daily_settlements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Manually trigger the daily settlement process.
    """
    result = await settlement_service.process_daily_settlements(db)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Settlement processing failed")
        )
    return result


@router.post("/process-manual/{company_id}", response_model=SettlementResponse)
async def process_manual_settlement(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insurance_user)
):
    """
    Manually trigger settlement for a specific insurance company.
    Insurance Admin only.
    """
    result = await settlement_service.process_manual_settlement(db, company_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Manual settlement processing failed")
        )

    return SettlementResponse(**result)
