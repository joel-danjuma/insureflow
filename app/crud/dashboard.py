from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.models import policy, premium, broker
from app.models.premium import PaymentStatus
from app.models.user import User, UserRole

def get_dashboard_kpis(db: Session, current_user: User):
    """
    Calculates and returns Key Performance Indicators based on the user's role.
    """
    today = date.today()
    start_of_month = today.replace(day=1)

    # Base queries that can be filtered
    policy_query = db.query(policy.Policy)
    premium_query = db.query(premium.Premium)

    if current_user.role == UserRole.BROKER:
        # A broker is linked via their separate Broker profile, not the user.id
        broker_profile = current_user.broker_profile
        if broker_profile:
            policy_query = policy_query.filter(policy.Policy.broker_id == broker_profile.id)
            premium_query = premium_query.join(policy.Policy).filter(policy.Policy.broker_id == broker_profile.id)
        else: # Broker has no profile, can see nothing
            return {"new_policies_this_month": 0, "outstanding_premiums_total": 0.0, "broker_count": 0}

    elif current_user.role == UserRole.CUSTOMER:
        policy_query = policy_query.filter(policy.Policy.user_id == current_user.id)
        premium_query = premium_query.join(policy.Policy).filter(policy.Policy.user_id == current_user.id)

    # Calculate KPIs based on the filtered queries
    new_policies_count = policy_query.filter(
        policy.Policy.start_date >= start_of_month
    ).count()

    outstanding_premiums = premium_query.with_entities(func.sum(premium.Premium.amount)).filter(
        premium.Premium.payment_status != PaymentStatus.PAID
    ).scalar() or 0.0
    
    # Broker count is only relevant for admins
    broker_count = db.query(func.count(broker.Broker.id)).scalar() if current_user.role == UserRole.ADMIN else 1

    return {
        "new_policies_this_month": new_policies_count,
        "outstanding_premiums_total": float(outstanding_premiums),
        "broker_count": broker_count,
    }

def get_recent_policies(db: Session, current_user: User, limit: int = 5):
    """
    Retrieves the most recent policies based on the user's role.
    """
    query = db.query(policy.Policy)
    if current_user.role == UserRole.BROKER:
        broker_profile = current_user.broker_profile
        if broker_profile:
            query = query.filter(policy.Policy.broker_id == broker_profile.id)
        else:
            return [] # No profile, no policies
    elif current_user.role == UserRole.CUSTOMER:
        query = query.filter(policy.Policy.user_id == current_user.id)
        
    return query.order_by(policy.Policy.start_date.desc()).limit(limit).all() 