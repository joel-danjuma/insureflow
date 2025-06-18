from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import dependencies
from app.crud import dashboard as crud_dashboard
from app.schemas import dashboard as schemas_dashboard
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=schemas_dashboard.DashboardData)
def get_dashboard_data(
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
):
    """
    Retrieve aggregated data for the main dashboard.
    """
    kpis = crud_dashboard.get_dashboard_kpis(db, current_user=current_user)
    recent_policies_db = crud_dashboard.get_recent_policies(db, current_user=current_user)
    
    recent_policies = [
        schemas_dashboard.RecentPolicy(
            policy_number=p.policy_number,
            customer_name=p.customer.full_name,
            broker=p.broker.name if p.broker else "N/A"
        ) for p in recent_policies_db
    ]

    return {
        "kpis": kpis,
        "recent_policies": recent_policies
    } 