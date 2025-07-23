"""
API endpoints for virtual account management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_active_user, get_current_broker_or_admin_user
from app.models.user import User
from app.schemas.virtual_account import (
    VirtualAccount, VirtualAccountSummary, VirtualAccountUpdate,
    IndividualVirtualAccountCreate, BusinessVirtualAccountCreate,
    VirtualAccountTransaction, PaymentSimulationRequest, PaymentSimulationResponse,
    BrokerPerformanceMetrics, CommissionSummary
)
from app.services.virtual_account_service import virtual_account_service
from app.crud import virtual_account as crud_virtual_account
import json

router = APIRouter()

@router.post("/individual", response_model=VirtualAccount, status_code=status.HTTP_201_CREATED)
async def create_individual_virtual_account(
    account_data: IndividualVirtualAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create an individual virtual account for the current user.
    """
    # Check if user already has a virtual account
    existing_accounts = crud_virtual_account.get_virtual_accounts_by_user(db, current_user.id)
    if existing_accounts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has virtual account(s). Use update endpoint to modify."
        )
    
    result = await virtual_account_service.create_individual_virtual_account(
        db=db,
        user=current_user,
        customer_identifier=account_data.customer_identifier
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result["virtual_account"]

@router.post("/business", response_model=VirtualAccount, status_code=status.HTTP_201_CREATED)
async def create_business_virtual_account(
    account_data: BusinessVirtualAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a business virtual account for the current user.
    """
    # Check if user already has a virtual account
    existing_accounts = crud_virtual_account.get_virtual_accounts_by_user(db, current_user.id)
    if existing_accounts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has virtual account(s). Use update endpoint to modify."
        )
    
    result = await virtual_account_service.create_business_virtual_account(
        db=db,
        user=current_user,
        business_name=account_data.business_name,
        customer_identifier=account_data.customer_identifier
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result["virtual_account"]

@router.get("/", response_model=List[VirtualAccountSummary])
def list_virtual_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    List virtual accounts. Admin users see all, brokers see only their own.
    """
    if current_user.can_perform_admin_actions:
        # Admin users can see all virtual accounts
        accounts = crud_virtual_account.get_active_virtual_accounts(db, skip=skip, limit=limit)
    else:
        # Brokers can only see their own virtual accounts
        accounts = crud_virtual_account.get_virtual_accounts_by_user(db, current_user.id)
    
    return accounts

@router.get("/me", response_model=List[VirtualAccount])
def get_my_virtual_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all virtual accounts for the current user.
    """
    accounts = crud_virtual_account.get_virtual_accounts_by_user(db, current_user.id)
    return accounts

@router.get("/{virtual_account_id}", response_model=VirtualAccount)
def get_virtual_account(
    virtual_account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific virtual account by ID.
    """
    account = crud_virtual_account.get_virtual_account(db, virtual_account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Virtual account not found")
    
    # Check permissions - users can only access their own accounts unless admin
    if account.user_id != current_user.id and not current_user.can_perform_admin_actions:
        raise HTTPException(status_code=403, detail="Not authorized to access this virtual account")
    
    return account

@router.put("/{virtual_account_id}", response_model=VirtualAccount)
def update_virtual_account(
    virtual_account_id: int,
    account_update: VirtualAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a virtual account.
    """
    account = crud_virtual_account.get_virtual_account(db, virtual_account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Virtual account not found")
    
    # Check permissions
    if account.user_id != current_user.id and not current_user.can_perform_admin_actions:
        raise HTTPException(status_code=403, detail="Not authorized to update this virtual account")
    
    # Update fields
    update_data = account_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    return account

@router.get("/{virtual_account_id}/transactions", response_model=List[VirtualAccountTransaction])
def get_virtual_account_transactions(
    virtual_account_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get transactions for a virtual account.
    """
    account = crud_virtual_account.get_virtual_account(db, virtual_account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Virtual account not found")
    
    # Check permissions
    if account.user_id != current_user.id and not current_user.can_perform_admin_actions:
        raise HTTPException(status_code=403, detail="Not authorized to access this virtual account")
    
    transactions = crud_virtual_account.get_virtual_account_transactions(
        db, virtual_account_id, skip=skip, limit=limit
    )
    return transactions

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def handle_virtual_account_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle incoming webhooks from Squad Co for virtual account transactions.
    """
    try:
        # Get the raw request body
        request_body = await request.body()
        
        # Parse the webhook payload
        payload = json.loads(request_body.decode('utf-8'))
        
        # Process the webhook
        result = virtual_account_service.process_webhook_transaction(db, payload)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {"status": "success", "message": "Webhook processed successfully"}
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.post("/simulate-payment", response_model=PaymentSimulationResponse)
async def simulate_payment(
    payment_request: PaymentSimulationRequest,
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Simulate a payment to a virtual account (sandbox only).
    """
    result = await virtual_account_service.simulate_payment(
        virtual_account_number=payment_request.virtual_account_number,
        amount=payment_request.amount
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return PaymentSimulationResponse(
        success=result.get("success", False),
        message=result.get("message"),
        data=result.get("data")
    )

@router.get("/performance/broker/{user_id}", response_model=BrokerPerformanceMetrics)
def get_broker_performance(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get performance metrics for a broker's virtual accounts.
    """
    # Check permissions - users can only see their own performance unless admin
    if user_id != current_user.id and not current_user.can_perform_admin_actions:
        raise HTTPException(status_code=403, detail="Not authorized to view this broker's performance")
    
    metrics = crud_virtual_account.get_broker_performance_metrics(db, user_id)
    return BrokerPerformanceMetrics(**metrics)

@router.get("/performance/top-brokers")
def get_top_brokers_performance(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get top performing brokers by commission earned.
    Only accessible by admin users.
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # This would need a more complex query to get top brokers
    # For now, return a placeholder
    return {"message": "Top brokers performance endpoint - implementation pending"}

@router.get("/commission/summary", response_model=CommissionSummary)
def get_commission_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get platform commission summary for InsureFlow and Habari.
    Only accessible by admin users.
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_platform_commission = crud_virtual_account.get_total_platform_commission(db)
    insureflow_commission = crud_virtual_account.get_total_commission_for_insureflow(db)
    habari_commission = crud_virtual_account.get_total_commission_for_habari(db)
    
    # Commission rates
    platform_rate = 0.01     # 1%
    insureflow_rate = 0.0075 # 0.75%
    habari_rate = 0.0025     # 0.25%
    
    return CommissionSummary(
        total_commission_pool=total_platform_commission,
        insureflow_commission=insureflow_commission,
        habari_commission=habari_commission,
        platform_commission_rate=platform_rate,
        insureflow_rate=insureflow_rate,
        habari_rate=habari_rate
    )

@router.post("/settlement/initiate/{virtual_account_id}")
async def initiate_manual_settlement(
    virtual_account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Manually initiate settlement for a virtual account.
    Only accessible by admin users.
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    account = crud_virtual_account.get_virtual_account(db, virtual_account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Virtual account not found")
    
    # This would initiate the settlement process
    # For now, return a placeholder
    return {"message": f"Settlement initiated for virtual account {virtual_account_id}"}

@router.get("/transactions/pending")
def get_pending_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get all pending transactions.
    Only accessible by admin users.
    """
    if not current_user.can_perform_admin_actions:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    transactions = crud_virtual_account.get_pending_transactions(db)
    return transactions 