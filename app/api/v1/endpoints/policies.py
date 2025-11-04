"""
API endpoints for policy management.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, timedelta, datetime
import logging

from app.core.database import get_db
from app.crud import policy as policy_crud
from app.crud import user as crud_user
from app.dependencies import (
    get_current_broker_or_admin_user, 
    get_current_policy_creator,
    get_current_active_user,
    get_current_payment_processor
)
from app.models.user import User, UserRole
from app.models.policy import Policy as PolicyModel, PolicyType, PolicyStatus, PaymentFrequency
from app.models.company import InsuranceCompany
from app.core.security import get_password_hash
from app.schemas.policy import Policy, PolicyCreate, PolicyUpdate, PolicySummary
from app.schemas.virtual_account import PaymentSimulationResponse
from app.services.virtual_account_service import virtual_account_service
from app.services.squad_co import squad_co_service
from app.models.virtual_account import VirtualAccount as VirtualAccountModel

logger = logging.getLogger(__name__)

router = APIRouter()

def _seed_mock_data(db: Session):
    """Seed database with mock policies and users that have all Squad API required fields."""
    existing_count = db.query(PolicyModel).count()
    if existing_count > 0:
        return  # Already seeded
    
    logger.info("📋 Seeding database with mock policies and users...")
    
    # Get or create default insurance company
    company = db.query(InsuranceCompany).filter(
        InsuranceCompany.name == "Secure Life Insurance Nigeria"
    ).first()
    
    if not company:
        company = InsuranceCompany(
            name="Secure Life Insurance Nigeria",
            registration_number="RC123456",
            address="14B Adeola Odeku Street, Victoria Island, Lagos",
            contact_email="info@securelife.ng",
            contact_phone="+234-1-234-5678",
            website="https://securelife.ng",
            description="Leading life insurance provider in Nigeria"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    
    # Create users with all Squad API required fields
    user_data = [
        {"full_name": "John Doe", "email": "john.doe@example.com", "phone": "08012345678", "gender": "male", "dob": date(1985, 3, 15)},
        {"full_name": "Jane Smith", "email": "jane.smith@example.com", "phone": "08023456789", "gender": "female", "dob": date(1990, 7, 22)},
        {"full_name": "Michael Johnson", "email": "michael.johnson@example.com", "phone": "08034567890", "gender": "male", "dob": date(1988, 11, 5)},
        {"full_name": "Sarah Williams", "email": "sarah.williams@example.com", "phone": "08045678901", "gender": "female", "dob": date(1992, 2, 18)},
        {"full_name": "David Brown", "email": "david.brown@example.com", "phone": "08056789012", "gender": "male", "dob": date(1987, 9, 30)},
        {"full_name": "Emily Davis", "email": "emily.davis@example.com", "phone": "08067890123", "gender": "female", "dob": date(1991, 4, 12)},
        {"full_name": "Robert Wilson", "email": "robert.wilson@example.com", "phone": "08078901234", "gender": "male", "dob": date(1986, 8, 25)},
        {"full_name": "Lisa Anderson", "email": "lisa.anderson@example.com", "phone": "08089012345", "gender": "female", "dob": date(1989, 12, 8)},
    ]
    
    users = []
    for user_info in user_data:
        user = crud_user.get_user_by_email(db, user_info["email"])
        if not user:
            user = User(
                username=user_info["email"].split("@")[0],
                email=user_info["email"],
                full_name=user_info["full_name"],
                phone_number=user_info["phone"],
                bvn="22222222222",  # Valid test BVN for Squad sandbox
                date_of_birth=datetime.combine(user_info["dob"], datetime.min.time()),
                gender=user_info["gender"],
                address="123 Fictional Street, Lagos, Nigeria",
                role=UserRole.CUSTOMER,
                hashed_password=get_password_hash("password123"),
                is_active=True,
                is_verified=True
            )
            db.add(user)
            users.append(user)
        else:
            users.append(user)
    
    db.commit()
    
    # Create policies linked to users
    policy_data = [
        {"name": "Life Insurance Policy", "number": "POL-001-2024-0001", "type": PolicyType.LIFE, "premium": Decimal("250000.00"), "due_date": date(2024, 12, 31), "frequency": PaymentFrequency.MONTHLY},
        {"name": "Auto Insurance Policy", "number": "POL-002-2024-0002", "type": PolicyType.AUTO, "premium": Decimal("180000.00"), "due_date": date(2024, 11, 15), "frequency": PaymentFrequency.QUARTERLY},
        {"name": "Health Insurance Policy", "number": "POL-003-2024-0003", "type": PolicyType.HEALTH, "premium": Decimal("120000.00"), "due_date": date(2024, 12, 15), "frequency": PaymentFrequency.MONTHLY},
        {"name": "Property Insurance Policy", "number": "POL-004-2024-0004", "type": PolicyType.HOME, "premium": Decimal("350000.00"), "due_date": date(2024, 12, 20), "frequency": PaymentFrequency.ANNUALLY},
        {"name": "Business Insurance Policy", "number": "POL-005-2024-0005", "type": PolicyType.BUSINESS, "premium": Decimal("500000.00"), "due_date": date(2024, 12, 10), "frequency": PaymentFrequency.QUARTERLY},
        {"name": "Travel Insurance Policy", "number": "POL-006-2024-0006", "type": PolicyType.TRAVEL, "premium": Decimal("75000.00"), "due_date": date(2024, 11, 30), "frequency": PaymentFrequency.ANNUALLY},
        {"name": "Marine Insurance Policy", "number": "POL-007-2024-0007", "type": PolicyType.TRAVEL, "premium": Decimal("450000.00"), "due_date": date(2024, 12, 25), "frequency": PaymentFrequency.QUARTERLY},
        {"name": "Professional Indemnity", "number": "POL-008-2024-0008", "type": PolicyType.BUSINESS, "premium": Decimal("200000.00"), "due_date": date(2024, 12, 5), "frequency": PaymentFrequency.ANNUALLY},
    ]
    
    for i, policy_info in enumerate(policy_data):
        existing = db.query(PolicyModel).filter(PolicyModel.policy_number == policy_info["number"]).first()
        if not existing:
            policy = PolicyModel(
                policy_name=policy_info["name"],
                policy_number=policy_info["number"],
                policy_type=policy_info["type"],
                company_id=company.id,
                user_id=users[i].id,
                premium_amount=policy_info["premium"],
                coverage_amount=policy_info["premium"] * 10,
                start_date=date.today(),
                due_date=policy_info["due_date"],
                end_date=policy_info["due_date"] + timedelta(days=365),
                payment_frequency=policy_info["frequency"],
                status=PolicyStatus.ACTIVE,
                payment_status="pending",
                company_name=f"{users[i].full_name.split()[0]} Corp",
                contact_person=users[i].full_name,
                contact_email=users[i].email,
                contact_phone=users[i].phone_number,
                merchant_reference=f"POL-{policy_info['number']}"
            )
            db.add(policy)
    
    db.commit()
    logger.info("✅ Mock data seeded successfully")

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
def get_policies(
    skip: int = 0,
    limit: int = 100,
    policy_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_broker_or_admin_user)
):
    """
    Get policies. Broker or Admin only.
    """
    # Seed database if empty
    _seed_mock_data(db)
    
    # Check user role and filter policies accordingly
    if current_user.role == UserRole.BROKER:
        if current_user.broker_profile:
            policies = policy_crud.get_policies_by_broker(
                db, broker_id=current_user.broker_profile.id, skip=skip, limit=limit
            )
        else:
            # If for some reason a broker user has no profile, return empty list
            policies = []
    elif current_user.can_perform_admin_actions:
        # Admin can see all policies
        policies = policy_crud.get_policies(db, skip=skip, limit=limit)
    else:
        # Fallback for unexpected roles
        policies = []

    return policies if policies is not None else []

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
    
    # Use the current user's ID to find the virtual account
    virtual_account = db.query(VirtualAccountModel).filter(VirtualAccountModel.user_id == current_user.id).first()
    if not virtual_account:
        raise HTTPException(status_code=404, detail="Virtual account not found for this user")

    # Call the centralized squad_co_service to handle the payment simulation
    # This service correctly handles the conversion of Naira to kobo.
    result = await squad_co_service.simulate_payment(
        virtual_account_number=virtual_account.virtual_account_number,
        amount=policy.premium_amount  # Pass the amount in Naira
    )
    
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@router.get("/{policy_id}/get-or-create-va", response_model=Dict[str, Any], tags=["Policies"])
async def get_or_create_policy_va(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves the virtual account for a policy's user, creating one if it doesn't exist.
    This endpoint is used by the frontend to populate the 'Pay Now' modal.
    """
    # 1. Find the policy
    policy = db.query(PolicyModel).filter(PolicyModel.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # 2. Get the associated user
    user = policy.user
    if not user:
        raise HTTPException(status_code=404, detail="User for this policy not found")

    # 3. Check for an existing VA for the user
    existing_va = db.query(VirtualAccountModel).filter(VirtualAccountModel.user_id == user.id).first()
    if existing_va:
        return {
            "success": True,
            "virtual_account": {
                "account_number": existing_va.virtual_account_number,
                "account_name": f"{existing_va.first_name} {existing_va.last_name}",
                "bank_name": "Squad Bank",  # Or lookup from bank_code if available
            }
        }
    
    # 4. If no VA exists, create one
    result = await virtual_account_service.create_individual_virtual_account(db=db, user=user, policy_id=policy.id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create VA for payment"))
    
    va_data = result.get("virtual_account", {})
    return {
        "success": True,
        "virtual_account": {
            "account_number": va_data.get("account_number"),
            "account_name": va_data.get("account_name"),
            "bank_name": va_data.get("bank_name"),
        }
    } 