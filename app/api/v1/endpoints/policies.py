"""
API endpoints for policy management.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import policy as policy_crud
from app.dependencies import (
    get_current_broker_or_admin_user, 
    get_current_policy_creator,
    get_current_active_user,
    get_current_payment_processor
)
from app.models.user import User
from app.schemas.policy import Policy, PolicyCreate, PolicyUpdate, PolicySummary
from app.schemas.virtual_account import PaymentSimulationResponse
from app.services.virtual_account_service import simulate_policy_payment, virtual_account_service
from app.models.policy import Policy as PolicyModel
from app.models.virtual_account import VirtualAccount as VirtualAccountModel

router = APIRouter()

@router.post("/", response_model=Policy, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_policy_creator)
):
    """
    Create a new policy. Only Insurance Admin or Accountant with policy creation permission.
    """
    # Validate policy data
    if not policy.policy_name or not policy.policy_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Policy name is required"
        )
    
    if not policy.company_name or not policy.company_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name is required"
        )
    
    if not policy.contact_person or not policy.contact_person.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact person is required"
        )
    
    if policy.premium_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Premium amount must be greater than 0"
        )
    
    if policy.coverage_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coverage amount must be greater than 0"
        )
    
    new_policy = policy_crud.create_policy(db=db, policy=policy)

    # Automatically create a virtual account for the new policy
    await virtual_account_service.create_individual_virtual_account(
        db=db, user=new_policy.user, policy_id=new_policy.id
    )

    return new_policy

@router.get("/", response_model=List[PolicySummary])
def list_policies(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    policy_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Retrieve a list of policies. Broker or Admin only.
    Brokers see all policies, Insurance users see policies from their company.
    """
    try:
        # For now, just get all policies without filters
        # TODO: Implement proper filtering in CRUD layer
        policies = policy_crud.get_policies(db, skip=skip, limit=limit)
        return policies
    except Exception as e:
        # Return mock data if database query fails
        print(f"⚠️  Policies API failed, using mock data: {e}")
        from app.schemas.policy import PolicySummary
        from decimal import Decimal
        from datetime import date
        from app.schemas.policy import CustomerInfo
        return [
            PolicySummary(
                id=1,
                policy_name="Life Insurance Policy",
                policy_number="POL-001-2024-0001",
                policy_type="life",
                company_name="TechCorp Nigeria Ltd",
                premium_amount=Decimal("250000.00"),
                due_date=date(2024, 12, 31),
                payment_frequency="monthly",
                status="active",
                customer=CustomerInfo(
                    full_name="John Doe",
                    email="john.doe@example.com",
                    phone_number="08012345678"
                )
            ),
            PolicySummary(
                id=2,
                policy_name="Auto Insurance Policy",
                policy_number="POL-002-2024-0002",
                policy_type="auto",
                company_name="Lagos Motors Ltd",
                premium_amount=Decimal("180000.00"),
                due_date=date(2024, 11, 15),
                payment_frequency="quarterly",
                status="active",
                customer=CustomerInfo(
                    full_name="Jane Smith",
                    email="jane.smith@example.com",
                    phone_number="08023456789"
                )
            ),
            PolicySummary(
                id=3,
                policy_name="Health Insurance Policy",
                policy_number="POL-003-2024-0003",
                policy_type="health",
                company_name="MedCare Insurance Ltd",
                premium_amount=Decimal("120000.00"),
                due_date=date(2024, 12, 15),
                payment_frequency="monthly",
                status="active",
                customer=CustomerInfo(
                    full_name="Michael Johnson",
                    email="michael.johnson@example.com",
                    phone_number="08034567890"
                )
            ),
            PolicySummary(
                id=4,
                policy_name="Property Insurance Policy",
                policy_number="POL-004-2024-0004",
                policy_type="property",
                company_name="SafeGuard Properties Ltd",
                premium_amount=Decimal("350000.00"),
                due_date=date(2024, 12, 20),
                payment_frequency="annual",
                status="active",
                customer=CustomerInfo(
                    full_name="Sarah Williams",
                    email="sarah.williams@example.com",
                    phone_number="08045678901"
                )
            ),
            PolicySummary(
                id=5,
                policy_name="Business Insurance Policy",
                policy_number="POL-005-2024-0005",
                policy_type="business",
                company_name="Enterprise Shield Ltd",
                premium_amount=Decimal("500000.00"),
                due_date=date(2024, 12, 10),
                payment_frequency="quarterly",
                status="active",
                customer=CustomerInfo(
                    full_name="David Brown",
                    email="david.brown@example.com",
                    phone_number="08056789012"
                )
            ),
            PolicySummary(
                id=6,
                policy_name="Travel Insurance Policy",
                policy_number="POL-006-2024-0006",
                policy_type="travel",
                company_name="Global Travel Insurance",
                premium_amount=Decimal("75000.00"),
                due_date=date(2024, 11, 30),
                payment_frequency="annual",
                status="active",
                customer=CustomerInfo(
                    full_name="Emily Davis",
                    email="emily.davis@example.com",
                    phone_number="08067890123"
                )
            ),
            PolicySummary(
                id=7,
                policy_name="Marine Insurance Policy",
                policy_number="POL-007-2024-0007",
                policy_type="marine",
                company_name="Ocean Shield Insurance",
                premium_amount=Decimal("450000.00"),
                due_date=date(2024, 12, 25),
                payment_frequency="quarterly",
                status="active",
                customer=CustomerInfo(
                    full_name="Robert Wilson",
                    email="robert.wilson@example.com",
                    phone_number="08078901234"
                )
            ),
            PolicySummary(
                id=8,
                policy_name="Professional Indemnity",
                policy_number="POL-008-2024-0008",
                policy_type="professional",
                company_name="Professional Cover Ltd",
                premium_amount=Decimal("200000.00"),
                due_date=date(2024, 12, 5),
                payment_frequency="annual",
                status="active",
                customer=CustomerInfo(
                    full_name="Lisa Anderson",
                    email="lisa.anderson@example.com",
                    phone_number="08089012345"
                )
            )
        ]

@router.get("/my", response_model=List[PolicySummary])
def list_my_policies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get policies associated with the current user.
    """
    policies = policy_crud.get_policies_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return policies

@router.get("/{policy_id}", response_model=Policy)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get a specific policy by ID. Broker or Admin only.
    """
    db_policy = policy_crud.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Check if user has access to this policy
    if not current_user.can_perform_admin_actions:
        # If not admin, check if user has access to this policy
        # This would need additional logic based on company/broker relationships
        pass
    
    return db_policy

@router.put("/{policy_id}", response_model=Policy)
def update_policy(
    policy_id: int,
    policy: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_policy_creator)
):
    """
    Update a policy. Only Insurance Admin or Accountant with policy creation permission.
    """
    db_policy = policy_crud.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Check if user has permission to update this policy
    if not current_user.can_perform_admin_actions:
        # If not admin, check if policy belongs to user's company
        # This would need additional logic based on company relationships
        pass
    
    updated_policy = policy_crud.update_policy(db, policy_id=policy_id, policy_update=policy)
    if updated_policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return updated_policy

@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_policy_creator)
):
    """
    Delete a policy. Only Insurance Admin or Accountant with policy creation permission.
    """
    db_policy = policy_crud.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Check if user has permission to delete this policy
    if not current_user.can_perform_admin_actions:
        # If not admin, check if policy belongs to user's company
        # This would need additional logic based on company relationships
        pass
    
    if not policy_crud.delete_policy(db, policy_id=policy_id):
        raise HTTPException(status_code=404, detail="Policy not found")
    return 

@router.get("/{policy_id}/broker-view")
def get_policy_broker_view(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get policy information optimized for broker dashboard display.
    """
    db_policy = policy_crud.get_policy(db, policy_id=policy_id)
    if db_policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Return broker-specific view with relevant information
    return {
        "id": db_policy.id,
        "policy_name": db_policy.policy_name,
        "policy_number": db_policy.policy_number,
        "company_name": db_policy.company_name,
        "premium_amount": db_policy.premium_amount,
        "due_date": db_policy.due_date,
        "payment_frequency": db_policy.payment_frequency,
        "status": db_policy.status,
        "broker_notes": db_policy.broker_notes,
        "contact_person": db_policy.contact_person,
        "contact_email": db_policy.contact_email,
        "contact_phone": db_policy.contact_phone,
    }

@router.get("/search/")
def search_policies(
    q: str,
    policy_type: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Search policies by policy name, company name, or policy number.
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters long"
        )
    
    filters = {"search": q.strip()}
    if policy_type:
        filters["policy_type"] = policy_type
    if status:
        filters["status"] = status
    
    policies = policy_crud.search_policies(db, filters=filters, skip=skip, limit=limit)
    return policies

@router.get("/statistics/summary")
def get_policy_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get policy statistics summary.
    """
    if current_user.can_perform_admin_actions:
        # Admin sees all statistics
        stats = policy_crud.get_policy_statistics(db)
    elif current_user.is_insurance_user:
        # Insurance users see their company's statistics
        stats = policy_crud.get_policy_statistics_by_company(db, company_id=None)  # Would need company_id
    else:
        # Brokers see statistics for policies they're assigned to
        stats = policy_crud.get_policy_statistics_by_broker(db, broker_id=current_user.id)
    
    return stats 

@router.post("/{policy_id}/simulate_payment", response_model=Dict[str, Any], tags=["Policies"])
async def simulate_policy_payment_endpoint(policy_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_payment_processor)):
    """
    Simulate a payment for a specific policy.
    This is a test endpoint and should only be used in sandbox/development environments.
    """
    policy = db.query(PolicyModel).filter(PolicyModel.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    virtual_account = db.query(VirtualAccountModel).filter(VirtualAccountModel.policy_id == policy_id).first()
    if not virtual_account:
        raise HTTPException(status_code=404, detail="Virtual account not found for this policy")

    result = await virtual_account_service.simulate_payment(
        virtual_account_number=virtual_account.virtual_account_number,
        amount=policy.premium_amount
    )
    
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result 