from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date

from app.models import policy, premium, user, broker

def get_dashboard_kpis(db: Session):
    """
    Calculates and returns the main Key Performance Indicators for the dashboard.
    """
    today = date.today()
    start_of_month = today.replace(day=1)

    new_policies_count = db.query(func.count(policy.Policy.id)).filter(
        policy.Policy.start_date >= start_of_month
    ).scalar()

    outstanding_premiums = db.query(func.sum(premium.Premium.amount)).filter(
        premium.Premium.payment_status != 'paid'
    ).scalar() or 0.0

    broker_count = db.query(func.count(broker.Broker.id)).scalar()

    return {
        "new_policies_this_month": new_policies_count,
        "outstanding_premiums_total": float(outstanding_premiums),
        "broker_count": broker_count,
    }

def get_recent_policies(db: Session, limit: int = 5):
    """
    Retrieves the most recent policies.
    """
    return db.query(policy.Policy).order_by(policy.Policy.start_date.desc()).limit(limit).all() 