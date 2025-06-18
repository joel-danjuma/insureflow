from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date

from app.models import policy, premium, user, broker
from app.models.premium import PaymentStatus
from app.models.user import User

def get_dashboard_kpis(db: Session, current_user: User):
    """
    Calculates and returns Key Performance Indicators based on the user's role.
    """
    today = date.today()
    start_of_month = today.replace(day=1)

    query_filters = []
    if current_user.role == "broker":
        query_filters.append(policy.Policy.broker_id == current_user.id)
    elif current_user.role == "customer":
        query_filters.append(policy.Policy.user_id == current_user.id)
    
    # Base query for policies
    policy_query = db.query(policy.Policy.id)
    if query_filters:
        policy_query = policy_query.filter(*query_filters)

    new_policies_count = policy_query.filter(
        policy.Policy.start_date >= start_of_month
    ).count()

    # Base query for premiums
    premium_query = db.query(func.sum(premium.Premium.amount))
    if query_filters:
        premium_query = premium_query.join(policy.Policy).filter(*query_filters)

    outstanding_premiums = premium_query.filter(
        premium.Premium.payment_status != PaymentStatus.PAID
    ).scalar() or 0.0

    broker_count = db.query(func.count(broker.Broker.id)).scalar()

    return {
        "new_policies_this_month": new_policies_count,
        "outstanding_premiums_total": float(outstanding_premiums),
        "broker_count": broker_count if current_user.role == "admin" else 1,
    }

def get_recent_policies(db: Session, current_user: User, limit: int = 5):
    """
    Retrieves the most recent policies based on the user's role.
    """
    query = db.query(policy.Policy)
    if current_user.role == "broker":
        query = query.filter(policy.Policy.broker_id == current_user.id)
    elif current_user.role == "customer":
        query = query.filter(policy.Policy.user_id == current_user.id)
        
    return query.order_by(policy.Policy.start_date.desc()).limit(limit).all() 