"""
CRUD operations for dashboard data and analytics.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal

from app.models import policy, premium, broker, user
from app.models.premium import PaymentStatus
from app.models.user import User, UserRole
from app.models.virtual_account import VirtualAccount, VirtualAccountStatus
from app.models.virtual_account_transaction import VirtualAccountTransaction, TransactionStatus, TransactionIndicator
from app.schemas.dashboard import (
    DashboardKPIS, EnhancedDashboardKPIS, ChartDataPoint, TimeSeriesData,
    PieChartData, BarChartData, BrokerPerformance, VirtualAccountSummary,
    RecentPolicy
)

def get_dashboard_kpis(db: Session, current_user: User) -> DashboardKPIS:
    """
    Calculate and return Key Performance Indicators based on the user's role.
    Enhanced with additional metrics.
    """
    today = date.today()
    start_of_month = today.replace(day=1)
    start_of_week = today - timedelta(days=today.weekday())

    # Base queries that can be filtered
    policy_query = db.query(policy.Policy)
    premium_query = db.query(premium.Premium)

    if current_user.role == UserRole.BROKER or current_user.is_broker_user:
        # Filter by broker
        broker_profile = current_user.broker_profile
        if broker_profile:
            policy_query = policy_query.filter(policy.Policy.broker_id == broker_profile.id)
            premium_query = premium_query.join(policy.Policy).filter(policy.Policy.broker_id == broker_profile.id)
        else:
            return _empty_kpis()

    elif current_user.role == UserRole.CUSTOMER:
        policy_query = policy_query.filter(policy.Policy.user_id == current_user.id)
        premium_query = premium_query.join(policy.Policy).filter(policy.Policy.user_id == current_user.id)

    # Calculate enhanced KPIs
    new_policies_count = policy_query.filter(
        policy.Policy.start_date >= start_of_month
    ).count()

    total_policies = policy_query.count()

    outstanding_premiums = premium_query.with_entities(func.sum(premium.Premium.amount)).filter(
        premium.Premium.payment_status != PaymentStatus.PAID
    ).scalar() or 0.0

    total_premium_collected = premium_query.with_entities(func.sum(premium.Premium.paid_amount)).filter(
        premium.Premium.payment_status == PaymentStatus.PAID
    ).scalar() or 0.0

    average_policy_value = float(total_premium_collected / total_policies) if total_policies > 0 else 0.0

    policies_due_this_week = policy_query.filter(
        and_(
            policy.Policy.due_date >= start_of_week,
            policy.Policy.due_date < start_of_week + timedelta(days=7)
        )
    ).count()

    overdue_payments = premium_query.filter(
        and_(
            premium.Premium.payment_status != PaymentStatus.PAID,
            premium.Premium.due_date < today
        )
    ).count()

    # Calculate conversion rate (simplified as paid vs total premiums)
    total_premiums = premium_query.count()
    paid_premiums = premium_query.filter(premium.Premium.payment_status == PaymentStatus.PAID).count()
    conversion_rate = float(paid_premiums / total_premiums * 100) if total_premiums > 0 else 0.0

    # Broker count
    broker_count = db.query(func.count(broker.Broker.id)).scalar() if current_user.can_perform_admin_actions else 1

    return DashboardKPIS(
        new_policies_this_month=new_policies_count,
        outstanding_premiums_total=float(outstanding_premiums),
        broker_count=broker_count,
        total_policies=total_policies,
        total_premium_collected=float(total_premium_collected),
        average_policy_value=average_policy_value,
        policies_due_this_week=policies_due_this_week,
        overdue_payments=overdue_payments,
        conversion_rate=conversion_rate
    )

def get_enhanced_dashboard_kpis(db: Session, current_user: User) -> EnhancedDashboardKPIS:
    """
    Get enhanced KPIs with virtual account and commission data.
    """
    base_kpis = get_dashboard_kpis(db, current_user)
    
    # Virtual account metrics
    virtual_accounts = db.query(VirtualAccount)
    if current_user.is_broker_user and not current_user.can_perform_admin_actions:
        virtual_accounts = virtual_accounts.filter(VirtualAccount.user_id == current_user.id)
    
    virtual_accounts_count = virtual_accounts.count()
    active_virtual_accounts = virtual_accounts.filter(
        VirtualAccount.status == VirtualAccountStatus.ACTIVE
    ).count()
    
    total_virtual_account_balance = virtual_accounts.with_entities(
        func.sum(VirtualAccount.current_balance)
    ).scalar() or 0.0
    
    # Platform commission metrics (InsureFlow + Habari split)
    total_platform_commission = virtual_accounts.with_entities(
        func.sum(VirtualAccount.total_credits * VirtualAccount.platform_commission_rate)
    ).scalar() or 0.0
    
    insureflow_commission_total = virtual_accounts.with_entities(
        func.sum(VirtualAccount.total_credits * VirtualAccount.insureflow_commission_rate)
    ).scalar() or 0.0
    
    habari_commission_total = virtual_accounts.with_entities(
        func.sum(VirtualAccount.total_credits * VirtualAccount.habari_commission_rate)
    ).scalar() or 0.0
    
    # Pending settlements
    pending_settlements = db.query(VirtualAccountTransaction).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.PENDING,
            VirtualAccountTransaction.transaction_indicator == TransactionIndicator.D
        )
    ).count()
    
    # Top performing broker (by transaction volume, not commission since that goes to platform)
    top_broker = db.query(broker.Broker).join(VirtualAccount).group_by(
        broker.Broker.id
    ).order_by(
        desc(func.sum(VirtualAccount.total_credits))
    ).first()
    
    top_performing_broker = top_broker.name if top_broker else None
    
    # Monthly growth rate (simplified calculation)
    today = date.today()
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month.replace(day=1)
    
    current_month_policies = db.query(policy.Policy).filter(
        policy.Policy.start_date >= today.replace(day=1)
    ).count()
    
    last_month_policies = db.query(policy.Policy).filter(
        and_(
            policy.Policy.start_date >= last_month_start,
            policy.Policy.start_date < today.replace(day=1)
        )
    ).count()
    
    monthly_growth_rate = float(
        (current_month_policies - last_month_policies) / last_month_policies * 100
    ) if last_month_policies > 0 else 0.0
    
    return EnhancedDashboardKPIS(
        **base_kpis.dict(),
        total_platform_commission=float(total_platform_commission),
        insureflow_commission_total=float(insureflow_commission_total),
        habari_commission_total=float(habari_commission_total),
        virtual_accounts_count=virtual_accounts_count,
        active_virtual_accounts=active_virtual_accounts,
        total_virtual_account_balance=float(total_virtual_account_balance),
        pending_settlements=pending_settlements,
        top_performing_broker=top_performing_broker,
        monthly_growth_rate=monthly_growth_rate
    )

def get_recent_policies(db: Session, current_user: User, limit: int = 5) -> List[RecentPolicy]:
    """
    Retrieve the most recent policies with enhanced information.
    """
    query = db.query(policy.Policy)
    
    if current_user.is_broker_user and not current_user.can_perform_admin_actions:
        broker_profile = current_user.broker_profile
        if broker_profile:
            query = query.filter(policy.Policy.broker_id == broker_profile.id)
        else:
            return []
    elif current_user.role == UserRole.CUSTOMER:
        query = query.filter(policy.Policy.user_id == current_user.id)
    
    policies = query.order_by(policy.Policy.created_at.desc()).limit(limit).all()
    
    recent_policies = []
    for p in policies:
        # Calculate total premium amount
        total_premium = db.query(func.sum(premium.Premium.amount)).filter(
            premium.Premium.policy_id == p.id
        ).scalar() or Decimal('0')
        
        # Calculate days until due
        days_until_due = None
        if p.due_date:
            days_until_due = (p.due_date - date.today()).days
        
        recent_policies.append(RecentPolicy(
            id=p.id,
            policy_number=p.policy_number,
            policy_name=p.policy_name or p.policy_number,
            customer_name=p.user.full_name if p.user else "Unknown",
            company_name=p.company_name or "N/A",
            broker=p.broker.name if p.broker else "N/A",
            premium_amount=float(total_premium),
            status=p.status.value,
            due_date=p.due_date,
            days_until_due=days_until_due
        ))
    
    return recent_policies

def get_policy_trends(db: Session, current_user: User, period: str = "monthly") -> TimeSeriesData:
    """
    Get policy creation trends over time.
    """
    today = date.today()
    
    if period == "daily":
        start_date = today - timedelta(days=30)
        date_format = "%Y-%m-%d"
        date_trunc = func.date(policy.Policy.created_at)
    elif period == "weekly":
        start_date = today - timedelta(weeks=12)
        date_format = "%Y-W%U"
        date_trunc = func.date_trunc('week', policy.Policy.created_at)
    else:  # monthly
        start_date = today - timedelta(days=365)
        date_format = "%Y-%m"
        date_trunc = func.date_trunc('month', policy.Policy.created_at)
    
    query = db.query(
        date_trunc.label('period'),
        func.count(policy.Policy.id).label('count')
    ).filter(
        policy.Policy.created_at >= start_date
    ).group_by('period').order_by('period')
    
    # Apply user-specific filters
    if current_user.is_broker_user and not current_user.can_perform_admin_actions:
        broker_profile = current_user.broker_profile
        if broker_profile:
            query = query.filter(policy.Policy.broker_id == broker_profile.id)
    
    results = query.all()
    
    data_points = []
    total = 0
    for result in results:
        period_date = result.period.date() if hasattr(result.period, 'date') else result.period
        data_points.append(ChartDataPoint(
            label=period_date.strftime(date_format),
            value=float(result.count),
            date=period_date
        ))
        total += result.count
    
    # Calculate growth rate
    growth_rate = 0.0
    if len(data_points) >= 2:
        latest = data_points[-1].value
        previous = data_points[-2].value
        growth_rate = ((latest - previous) / previous * 100) if previous > 0 else 0.0
    
    return TimeSeriesData(
        period=period,
        data_points=data_points,
        total=float(total),
        growth_rate=growth_rate
    )

def get_policy_type_distribution(db: Session, current_user: User) -> PieChartData:
    """
    Get distribution of policies by type.
    """
    query = db.query(
        policy.Policy.policy_type,
        func.count(policy.Policy.id).label('count')
    ).group_by(policy.Policy.policy_type)
    
    # Apply user-specific filters
    if current_user.is_broker_user and not current_user.can_perform_admin_actions:
        broker_profile = current_user.broker_profile
        if broker_profile:
            query = query.filter(policy.Policy.broker_id == broker_profile.id)
    
    results = query.all()
    
    segments = []
    total = 0
    for result in results:
        count = result.count
        segments.append(ChartDataPoint(
            label=result.policy_type.value.title(),
            value=float(count)
        ))
        total += count
    
    return PieChartData(
        segments=segments,
        total=float(total)
    )

def get_broker_performance_list(db: Session, current_user: User, limit: int = 10) -> List[BrokerPerformance]:
    """
    Get top performing brokers with detailed metrics.
    """
    if not current_user.can_perform_admin_actions and not current_user.is_insurance_user:
        # Non-admin, non-insurance users can only see their own performance
        if current_user.broker_profile:
            return [get_broker_individual_performance(db, current_user.broker_profile.id)]
        return []
    
    # Get broker performance data
    broker_stats = db.query(
        broker.Broker.id,
        broker.Broker.name,
        broker.Broker.agency_name,
        func.count(policy.Policy.id).label('total_policies'),
        func.sum(premium.Premium.amount).label('total_premiums'),
        func.sum(premium.Premium.paid_amount).label('total_paid')
    ).outerjoin(
        policy.Policy, broker.Broker.id == policy.Policy.broker_id
    ).outerjoin(
        premium.Premium, policy.Policy.id == premium.Premium.policy_id
    ).group_by(
        broker.Broker.id, broker.Broker.name, broker.Broker.agency_name
    ).order_by(
        desc('total_premiums')
    ).limit(limit).all()
    
    performance_list = []
    for rank, stats in enumerate(broker_stats, 1):
        # Calculate additional metrics
        commission_rate = 0.01  # 1% commission
        commission_earned = float(stats.total_paid or 0) * commission_rate
        
        conversion_rate = 0.0
        if stats.total_policies and stats.total_premiums:
            paid_policies = db.query(policy.Policy).join(premium.Premium).filter(
                and_(
                    policy.Policy.broker_id == stats.id,
                    premium.Premium.payment_status == PaymentStatus.PAID
                )
            ).count()
            conversion_rate = (paid_policies / stats.total_policies) * 100
        
        average_deal_size = float(stats.total_premiums / stats.total_policies) if stats.total_policies else 0.0
        
        # Get last activity
        last_policy = db.query(policy.Policy).filter(
            policy.Policy.broker_id == stats.id
        ).order_by(desc(policy.Policy.created_at)).first()
        
        last_activity = last_policy.created_at if last_policy else None
        
        performance_list.append(BrokerPerformance(
            broker_id=stats.id,
            broker_name=stats.name,
            organization_name=stats.agency_name,
            total_policies=stats.total_policies or 0,
            total_premiums=float(stats.total_premiums or 0),
            commission_earned=commission_earned,
            conversion_rate=conversion_rate,
            client_retention_rate=85.0,  # Placeholder - would need more complex calculation
            average_deal_size=average_deal_size,
            last_activity=last_activity,
            rank=rank
        ))
    
    return performance_list

def get_broker_individual_performance(db: Session, broker_id: int) -> BrokerPerformance:
    """
    Get performance metrics for a specific broker.
    """
    broker_obj = db.query(broker.Broker).filter(broker.Broker.id == broker_id).first()
    if not broker_obj:
        raise ValueError("Broker not found")
    
    # Calculate metrics
    total_policies = db.query(policy.Policy).filter(policy.Policy.broker_id == broker_id).count()
    
    total_premiums = db.query(func.sum(premium.Premium.amount)).join(policy.Policy).filter(
        policy.Policy.broker_id == broker_id
    ).scalar() or 0
    
    total_paid = db.query(func.sum(premium.Premium.paid_amount)).join(policy.Policy).filter(
        and_(
            policy.Policy.broker_id == broker_id,
            premium.Premium.payment_status == PaymentStatus.PAID
        )
    ).scalar() or 0
    
    commission_earned = float(total_paid) * 0.01  # 1% commission
    
    # Conversion rate
    paid_policies = db.query(policy.Policy).join(premium.Premium).filter(
        and_(
            policy.Policy.broker_id == broker_id,
            premium.Premium.payment_status == PaymentStatus.PAID
        )
    ).count()
    
    conversion_rate = (paid_policies / total_policies * 100) if total_policies > 0 else 0.0
    
    return BrokerPerformance(
        broker_id=broker_id,
        broker_name=broker_obj.name,
        organization_name=broker_obj.agency_name,
        total_policies=total_policies,
        total_premiums=float(total_premiums),
        commission_earned=commission_earned,
        conversion_rate=conversion_rate,
        client_retention_rate=85.0,  # Placeholder
        average_deal_size=float(total_premiums / total_policies) if total_policies > 0 else 0.0,
        last_activity=None,  # Would need to calculate
        rank=1
    )

def get_virtual_account_summaries(db: Session, current_user: User, limit: int = 5) -> List[VirtualAccountSummary]:
    """
    Get virtual account summaries for dashboard.
    """
    query = db.query(VirtualAccount)
    
    if current_user.is_broker_user and not current_user.can_perform_admin_actions:
        query = query.filter(VirtualAccount.user_id == current_user.id)
    
    accounts = query.order_by(desc(VirtualAccount.current_balance)).limit(limit).all()
    
    summaries = []
    for account in accounts:
        # Get last transaction
        last_transaction = db.query(VirtualAccountTransaction).filter(
            VirtualAccountTransaction.virtual_account_id == account.id
        ).order_by(desc(VirtualAccountTransaction.created_at)).first()
        
        summaries.append(VirtualAccountSummary(
            account_id=account.id,
            account_number=account.virtual_account_number,
            account_type=account.account_type.value,
            current_balance=float(account.current_balance),
            total_credits=float(account.total_credits),
            platform_commission_earned=float(account.total_platform_commission),
            last_transaction=last_transaction.created_at if last_transaction else None,
            status=account.status.value
        ))
    
    return summaries

def _empty_kpis() -> DashboardKPIS:
    """Return empty KPIs for users with no data access."""
    return DashboardKPIS(
        new_policies_this_month=0,
        outstanding_premiums_total=0.0,
        broker_count=0,
        total_policies=0,
        total_premium_collected=0.0,
        average_policy_value=0.0,
        policies_due_this_week=0,
        overdue_payments=0,
        conversion_rate=0.0
    ) 