"""
API endpoints for settlement management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_user, get_current_insurance_user
from app.models.user import User
from app.services.settlement_service import settlement_service
from app.services.gaps_service import get_gaps_client
from app.schemas.settlement import (
    SettlementResponse, 
    SettlementSummary, 
    GAPSTestResponse,
    ManualSettlementRequest
)

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


@router.get("/summary", response_model=SettlementSummary)
def get_settlement_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to summarize"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get settlement summary for the specified period.
    Admin only.
    """
    settlement_processor = get_settlement_processor()
    result = settlement_processor.get_settlement_summary(db, days)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to generate settlement summary")
        )
    
    return SettlementSummary(**result)


@router.get("/status/{settlement_reference}")
def get_settlement_status(
    settlement_reference: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Query GAPS for settlement status by reference.
    Admin only.
    """
    settlement_processor = get_settlement_processor()
    result = settlement_processor.query_settlement_status(settlement_reference)
    
    return {
        "settlement_reference": settlement_reference,
        "gaps_response": result
    }


@router.get("/test-gaps-connection", response_model=GAPSTestResponse)
def test_gaps_connection(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Test GAPS API connection and configuration.
    Admin only.
    """
    try:
        gaps_client = get_gaps_client()
        
        # Test account validation (using a dummy GTB account)
        test_result = gaps_client.validate_account("0123456789")
        
        return GAPSTestResponse(
            connection_status="SUCCESS" if test_result["success"] else "FAILED",
            gaps_response=test_result,
            message="GAPS connection test completed"
        )
        
    except Exception as e:
        return GAPSTestResponse(
            connection_status="ERROR",
            gaps_response={"error": str(e)},
            message=f"GAPS connection test failed: {str(e)}"
        )


@router.get("/transactions/pending")
def get_pending_transactions(
    company_id: Optional[int] = Query(None, description="Filter by insurance company ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get all transactions pending settlement.
    Admin only.
    """
    settlement_processor = get_settlement_processor()
    
    try:
        # Get pending settlements
        settlements = settlement_processor.get_pending_settlements(
            db, 
            company_id=company_id
        )
        
        return {
            "success": True,
            "pending_settlements": settlements,
            "total_companies": len(settlements),
            "total_amount": sum(s["net_settlement"] for s in settlements)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pending transactions: {str(e)}"
        )


@router.post("/query-gaps-transaction/{transaction_ref}")
def query_gaps_transaction(
    transaction_ref: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Query specific GAPS transaction status.
    Admin only.
    """
    try:
        gaps_client = get_gaps_client()
        result = gaps_client.query_transaction(transaction_ref)
        
        return {
            "transaction_reference": transaction_ref,
            "gaps_response": result,
            "timestamp": "2024-01-01T00:00:00Z"  # Current timestamp
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query GAPS transaction: {str(e)}"
        )
