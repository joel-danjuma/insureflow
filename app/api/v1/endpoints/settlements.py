"""
API endpoints for settlement management.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_user, get_current_insureflow_admin_user
from app.models.user import User
from app.services.settlement_service import settlement_service
from app.services.gaps_service import gaps_service

router = APIRouter()

@router.post("/process-daily", response_model=Dict[str, Any])
async def process_daily_settlements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin_user)
):
    """
    Process daily settlements for all insurance firms.
    InsureFlow Admin only.
    """
    result = await settlement_service.process_daily_settlements(db)
    
    if result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result

@router.post("/process-manual/{firm_id}", response_model=Dict[str, Any])
async def process_manual_settlement(
    firm_id: int,
    transaction_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin_user)
):
    """
    Process manual settlement for a specific insurance firm.
    InsureFlow Admin only.
    """
    result = await settlement_service.process_manual_settlement(
        db, firm_id, transaction_ids
    )
    
    if result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result

@router.get("/summary", response_model=Dict[str, Any])
def get_settlement_summary(
    days: int = Query(7, ge=1, le=90, description="Number of days to include in summary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get settlement summary for the specified period.
    Admin only.
    """
    result = settlement_service.get_settlement_summary(db, days)
    
    if result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result

@router.get("/status", response_model=Dict[str, Any])
async def get_settlement_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get settlement service status and configuration.
    Admin only.
    """
    from app.core.config import settings
    
    # Check GAPS service configuration
    gaps_configured = all([
        settings.GAPS_CUSTOMER_ID,
        settings.GAPS_USERNAME,
        settings.GAPS_PASSWORD
    ])
    
    # Check Squad service configuration
    squad_configured = bool(settings.SQUAD_SECRET_KEY)
    
    return {
        "settlement_service_status": "operational",
        "gaps_configured": gaps_configured,
        "squad_configured": squad_configured,
        "auto_settlement_enabled": settings.AUTO_SETTLEMENT_ENABLED,
        "commission_rate": settings.PLATFORM_COMMISSION_RATE,
        "settlement_threshold": settings.SETTLEMENT_THRESHOLD,
        "settlement_account": settings.INSUREFLOW_SETTLEMENT_ACCOUNT or "Not configured"
    }

@router.post("/test-gaps-connection", response_model=Dict[str, Any])
async def test_gaps_connection(
    current_user: User = Depends(get_current_insureflow_admin_user)
):
    """
    Test GAPS API connection and authentication.
    InsureFlow Admin only.
    """
    # Test with a dummy account validation
    result = await gaps_service.validate_account("1234567890", "058152052")
    
    return {
        "gaps_connection_test": result.get("success", False),
        "message": result.get("message", result.get("error", "Unknown result")),
        "details": result
    }

@router.get("/transactions/pending", response_model=List[Dict[str, Any]])
def get_pending_transactions(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of transactions to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get pending settlement transactions.
    Admin only.
    """
    from app.models.virtual_account_transaction import VirtualAccountTransaction, TransactionStatus
    from app.models.virtual_account import VirtualAccount
    from app.models.policy import Policy
    from app.models.company import InsuranceCompany
    
    # Get pending transactions with related data
    pending_transactions = db.query(VirtualAccountTransaction)\
        .filter(
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
            VirtualAccountTransaction.settlement_status == 'pending'
        )\
        .order_by(VirtualAccountTransaction.transaction_date.desc())\
        .limit(limit)\
        .all()
    
    result = []
    for transaction in pending_transactions:
        # Get related virtual account and policy
        virtual_account = db.query(VirtualAccount).filter(
            VirtualAccount.id == transaction.virtual_account_id
        ).first()
        
        if virtual_account and virtual_account.policy:
            policy = virtual_account.policy
            firm = db.query(InsuranceCompany).filter(
                InsuranceCompany.id == policy.company_id
            ).first()
            
            result.append({
                "transaction_id": transaction.id,
                "amount": float(transaction.settled_amount),
                "transaction_date": transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                "policy_number": policy.policy_number,
                "policy_id": policy.id,
                "firm_name": firm.name if firm else "Unknown",
                "firm_id": policy.company_id,
                "customer_name": policy.contact_person,
                "reference": transaction.transaction_reference
            })
    
    return result

@router.post("/query-gaps-transaction", response_model=Dict[str, Any])
async def query_gaps_transaction(
    transaction_ref: str,
    current_user: User = Depends(get_current_insureflow_admin_user)
):
    """
    Query the status of a GAPS transaction.
    InsureFlow Admin only.
    """
    result = await gaps_service.query_transaction_status(transaction_ref)
    
    return {
        "transaction_reference": transaction_ref,
        "query_result": result
    }
