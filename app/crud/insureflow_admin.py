"""
CRUD operations for InsureFlow internal admin dashboard.
Handles transaction monitoring, commission analytics, and platform management.
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from sqlalchemy.sql import text

from app.models.virtual_account import VirtualAccount, VirtualAccountStatus
from app.models.virtual_account_transaction import VirtualAccountTransaction, TransactionType, TransactionStatus, TransactionIndicator
from app.models.user import User, UserRole
from app.models.policy import Policy, PolicyStatus
from app.models.premium import Premium
from app.schemas.dashboard import (
    TransactionLogEntry, CommissionAnalytics, PlatformHealthMetrics,
    FinancialReport, UserManagementSummary, TransactionFilter,
    SystemAlert, AuditLogEntry
)


def get_transaction_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[TransactionFilter] = None
) -> List[TransactionLogEntry]:
    """
    Get transaction logs with filtering and pagination for admin monitoring.
    """
    query = db.query(
        VirtualAccountTransaction,
        VirtualAccount.virtual_account_number,
        User.first_name,
        User.last_name,
        User.username
    ).join(
        VirtualAccount, VirtualAccountTransaction.virtual_account_id == VirtualAccount.id
    ).join(
        User, VirtualAccount.user_id == User.id
    )
    
    # Apply filters
    if filters:
        if filters.start_date:
            query = query.filter(VirtualAccountTransaction.transaction_date >= filters.start_date)
        if filters.end_date:
            query = query.filter(VirtualAccountTransaction.transaction_date <= filters.end_date)
        if filters.transaction_type:
            query = query.filter(VirtualAccountTransaction.transaction_type == filters.transaction_type)
        if filters.status:
            query = query.filter(VirtualAccountTransaction.status == filters.status)
        if filters.min_amount:
            query = query.filter(VirtualAccountTransaction.principal_amount >= filters.min_amount)
        if filters.max_amount:
            query = query.filter(VirtualAccountTransaction.principal_amount <= filters.max_amount)
        if filters.user_id:
            query = query.filter(User.id == filters.user_id)
        if filters.virtual_account_id:
            query = query.filter(VirtualAccount.id == filters.virtual_account_id)
        if filters.policy_id:
            query = query.filter(VirtualAccountTransaction.policy_id == filters.policy_id)
    
    # Order by most recent first
    query = query.order_by(desc(VirtualAccountTransaction.created_at))
    
    # Apply pagination
    results = query.offset(skip).limit(limit).all()
    
    # Transform to TransactionLogEntry
    logs = []
    for transaction, account_number, first_name, last_name, username in results:
        user_name = f"{first_name or ''} {last_name or ''}".strip() or username
        
        logs.append(TransactionLogEntry(
            id=transaction.id,
            transaction_reference=transaction.transaction_reference,
            virtual_account_number=account_number,
            user_name=user_name,
            transaction_type=transaction.transaction_type.value,
            transaction_indicator=transaction.transaction_indicator.value,
            status=transaction.status.value,
            principal_amount=transaction.principal_amount,
            settled_amount=transaction.settled_amount,
            fee_charged=transaction.fee_charged,
            total_platform_commission=transaction.total_platform_commission,
            insureflow_commission=transaction.insureflow_commission,
            habari_commission=transaction.habari_commission,
            currency=transaction.currency,
            sender_name=transaction.sender_name,
            transaction_date=transaction.transaction_date,
            webhook_received_at=transaction.webhook_received_at,
            policy_id=transaction.policy_id,
            created_at=transaction.created_at
        ))
    
    return logs


def get_commission_analytics(db: Session) -> CommissionAnalytics:
    """
    Calculate comprehensive commission analytics for InsureFlow.
    """
    # Total InsureFlow revenue (0.75% of all transactions)
    total_revenue = db.query(
        func.sum(VirtualAccountTransaction.insureflow_commission)
    ).filter(
        VirtualAccountTransaction.status == TransactionStatus.COMPLETED
    ).scalar() or Decimal('0')
    
    # Monthly revenue (current month)
    current_month_start = date.today().replace(day=1)
    monthly_revenue = db.query(
        func.sum(VirtualAccountTransaction.insureflow_commission)
    ).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
            VirtualAccountTransaction.transaction_date >= current_month_start
        )
    ).scalar() or Decimal('0')
    
    # Daily revenue (today)
    today = date.today()
    daily_revenue = db.query(
        func.sum(VirtualAccountTransaction.insureflow_commission)
    ).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
            func.date(VirtualAccountTransaction.transaction_date) == today
        )
    ).scalar() or Decimal('0')
    
    # Revenue growth rate (comparing this month to last month)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = current_month_start - timedelta(days=1)
    
    last_month_revenue = db.query(
        func.sum(VirtualAccountTransaction.insureflow_commission)
    ).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
            VirtualAccountTransaction.transaction_date >= last_month_start,
            VirtualAccountTransaction.transaction_date <= last_month_end
        )
    ).scalar() or Decimal('0')
    
    revenue_growth_rate = float(
        (monthly_revenue - last_month_revenue) / last_month_revenue * 100
    ) if last_month_revenue > 0 else 0.0
    
    # Average commission per transaction
    transaction_count = db.query(
        func.count(VirtualAccountTransaction.id)
    ).filter(
        VirtualAccountTransaction.status == TransactionStatus.COMPLETED
    ).scalar() or 0
    
    avg_commission = total_revenue / transaction_count if transaction_count > 0 else Decimal('0')
    
    # Top revenue generating brokers (based on transaction volume from their VAs)
    top_brokers = db.query(
        User.id,
        User.first_name,
        User.last_name,
        User.username,
        func.sum(VirtualAccountTransaction.insureflow_commission).label('total_commission'),
        func.count(VirtualAccountTransaction.id).label('transaction_count')
    ).join(
        VirtualAccount, User.id == VirtualAccount.user_id
    ).join(
        VirtualAccountTransaction, VirtualAccount.id == VirtualAccountTransaction.virtual_account_id
    ).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
            User.role.in_([UserRole.BROKER, UserRole.BROKER_ADMIN, UserRole.BROKER_ACCOUNTANT])
        )
    ).group_by(
        User.id, User.first_name, User.last_name, User.username
    ).order_by(
        desc('total_commission')
    ).limit(10).all()
    
    top_revenue_brokers = [
        {
            "user_id": broker.id,
            "name": f"{broker.first_name or ''} {broker.last_name or ''}".strip() or broker.username,
            "total_commission": float(broker.total_commission),
            "transaction_count": broker.transaction_count
        }
        for broker in top_brokers
    ]
    
    # Monthly trends (last 12 months)
    monthly_trends = []
    for i in range(12):
        month_start = (current_month_start - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_revenue = db.query(
            func.sum(VirtualAccountTransaction.insureflow_commission)
        ).filter(
            and_(
                VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
                VirtualAccountTransaction.transaction_date >= month_start,
                VirtualAccountTransaction.transaction_date <= month_end
            )
        ).scalar() or Decimal('0')
        
        monthly_trends.append({
            "month": month_start.strftime("%Y-%m"),
            "revenue": float(month_revenue)
        })
    
    monthly_trends.reverse()  # Chronological order
    
    return CommissionAnalytics(
        total_revenue_generated=total_revenue,
        monthly_revenue=monthly_revenue,
        daily_revenue=daily_revenue,
        revenue_growth_rate=revenue_growth_rate,
        avg_commission_per_transaction=avg_commission,
        top_revenue_generating_brokers=top_revenue_brokers,
        monthly_trends=monthly_trends
    )


def get_platform_health_metrics(db: Session) -> PlatformHealthMetrics:
    """
    Get platform health and monitoring metrics.
    """
    # User metrics
    total_active_users = db.query(User).filter(User.is_active == True).count()
    
    # Virtual account metrics
    total_virtual_accounts = db.query(VirtualAccount).count()
    active_virtual_accounts = db.query(VirtualAccount).filter(
        VirtualAccount.status == VirtualAccountStatus.ACTIVE
    ).count()
    
    # Transaction metrics
    today = date.today()
    failed_transactions_today = db.query(VirtualAccountTransaction).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.FAILED,
            func.date(VirtualAccountTransaction.transaction_date) == today
        )
    ).count()
    
    pending_settlements = db.query(VirtualAccountTransaction).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.PENDING,
            VirtualAccountTransaction.transaction_type == TransactionType.SETTLEMENT
        )
    ).count()
    
    # Total transaction volume
    total_transaction_volume = db.query(
        func.sum(VirtualAccountTransaction.principal_amount)
    ).filter(
        VirtualAccountTransaction.status == TransactionStatus.COMPLETED
    ).scalar() or Decimal('0')
    
    # Webhook success rate (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    total_webhooks = db.query(VirtualAccountTransaction).filter(
        VirtualAccountTransaction.webhook_received_at >= yesterday
    ).count()
    
    successful_webhooks = db.query(VirtualAccountTransaction).filter(
        and_(
            VirtualAccountTransaction.webhook_received_at >= yesterday,
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED
        )
    ).count()
    
    webhook_success_rate = (successful_webhooks / total_webhooks * 100) if total_webhooks > 0 else 100.0
    
    # Processing errors (recent failed transactions)
    processing_errors = db.query(
        VirtualAccountTransaction.id,
        VirtualAccountTransaction.transaction_reference,
        VirtualAccountTransaction.remarks,
        VirtualAccountTransaction.created_at
    ).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.FAILED,
            VirtualAccountTransaction.created_at >= yesterday
        )
    ).order_by(desc(VirtualAccountTransaction.created_at)).limit(10).all()
    
    error_list = [
        {
            "transaction_id": error.id,
            "reference": error.transaction_reference,
            "error_message": error.remarks or "Unknown error",
            "timestamp": error.created_at
        }
        for error in processing_errors
    ]
    
    return PlatformHealthMetrics(
        total_active_users=total_active_users,
        total_virtual_accounts=total_virtual_accounts,
        active_virtual_accounts=active_virtual_accounts,
        webhook_success_rate=webhook_success_rate,
        failed_transactions_today=failed_transactions_today,
        pending_settlements=pending_settlements,
        system_uptime="99.9%",  # This would be calculated from monitoring data
        api_response_time=150.0,  # This would come from monitoring tools
        total_transaction_volume=total_transaction_volume,
        processing_errors=error_list
    )


def get_financial_report(db: Session, period: str = "monthly") -> FinancialReport:
    """
    Generate financial report for accounting and reconciliation.
    """
    # Determine date range based on period
    if period == "daily":
        start_date = date.today()
        end_date = start_date
        report_period = start_date.strftime("%Y-%m-%d")
    elif period == "monthly":
        start_date = date.today().replace(day=1)
        end_date = date.today()
        report_period = start_date.strftime("%Y-%m")
    else:  # yearly
        start_date = date.today().replace(month=1, day=1)
        end_date = date.today()
        report_period = str(start_date.year)
    
    # Transaction metrics
    transactions = db.query(VirtualAccountTransaction).filter(
        and_(
            func.date(VirtualAccountTransaction.transaction_date) >= start_date,
            func.date(VirtualAccountTransaction.transaction_date) <= end_date,
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED
        )
    )
    
    total_transactions = transactions.count()
    
    # Financial metrics
    gross_transaction_volume = transactions.with_entities(
        func.sum(VirtualAccountTransaction.principal_amount)
    ).scalar() or Decimal('0')
    
    total_fees_collected = transactions.with_entities(
        func.sum(VirtualAccountTransaction.fee_charged)
    ).scalar() or Decimal('0')
    
    insureflow_commission_earned = transactions.with_entities(
        func.sum(VirtualAccountTransaction.insureflow_commission)
    ).scalar() or Decimal('0')
    
    habari_commission_paid = transactions.with_entities(
        func.sum(VirtualAccountTransaction.habari_commission)
    ).scalar() or Decimal('0')
    
    net_revenue = insureflow_commission_earned - total_fees_collected
    
    # Pending settlements
    pending_settlements = db.query(
        func.sum(VirtualAccountTransaction.settled_amount)
    ).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.PENDING,
            VirtualAccountTransaction.transaction_type == TransactionType.SETTLEMENT
        )
    ).scalar() or Decimal('0')
    
    # Transaction breakdown by type
    transaction_breakdown = {}
    for tx_type in TransactionType:
        count = transactions.filter(
            VirtualAccountTransaction.transaction_type == tx_type
        ).count()
        transaction_breakdown[tx_type.value] = count
    
    # Top policies by transaction volume
    top_policies = db.query(
        Policy.id,
        Policy.policy_name,
        Policy.company_name,
        func.sum(VirtualAccountTransaction.principal_amount).label('total_volume'),
        func.count(VirtualAccountTransaction.id).label('transaction_count')
    ).join(
        VirtualAccountTransaction, Policy.id == VirtualAccountTransaction.policy_id
    ).filter(
        and_(
            func.date(VirtualAccountTransaction.transaction_date) >= start_date,
            func.date(VirtualAccountTransaction.transaction_date) <= end_date,
            VirtualAccountTransaction.status == TransactionStatus.COMPLETED
        )
    ).group_by(
        Policy.id, Policy.policy_name, Policy.company_name
    ).order_by(
        desc('total_volume')
    ).limit(10).all()
    
    top_policies_list = [
        {
            "policy_id": policy.id,
            "policy_name": policy.policy_name,
            "company_name": policy.company_name,
            "total_volume": float(policy.total_volume),
            "transaction_count": policy.transaction_count
        }
        for policy in top_policies
    ]
    
    return FinancialReport(
        report_period=report_period,
        total_transactions=total_transactions,
        gross_transaction_volume=gross_transaction_volume,
        total_fees_collected=total_fees_collected,
        insureflow_commission_earned=insureflow_commission_earned,
        habari_commission_paid=habari_commission_paid,
        net_revenue=net_revenue,
        pending_settlements=pending_settlements,
        transaction_breakdown=transaction_breakdown,
        top_policies=top_policies_list
    )


def get_user_management_summary(db: Session) -> UserManagementSummary:
    """
    Get user management summary for admin oversight.
    """
    # User counts by role
    total_users = db.query(User).count()
    insurance_companies = db.query(User).filter(
        User.role.in_([UserRole.INSURANCE_ADMIN, UserRole.INSURANCE_ACCOUNTANT])
    ).count()
    brokers = db.query(User).filter(
        User.role.in_([UserRole.BROKER, UserRole.BROKER_ADMIN, UserRole.BROKER_ACCOUNTANT])
    ).count()
    
    # New users this month
    current_month_start = date.today().replace(day=1)
    new_users_this_month = db.query(User).filter(
        User.created_at >= current_month_start
    ).count()
    
    # Active users today (users with recent login)
    today = date.today()
    active_users_today = db.query(User).filter(
        and_(
            User.is_active == True,
            func.date(User.last_login) == today
        )
    ).count()
    
    # Users with virtual accounts
    users_with_virtual_accounts = db.query(User).join(VirtualAccount).distinct().count()
    
    # Top active users (by transaction volume)
    top_active_users = db.query(
        User.id,
        User.first_name,
        User.last_name,
        User.username,
        User.role,
        func.count(VirtualAccountTransaction.id).label('transaction_count'),
        func.sum(VirtualAccountTransaction.principal_amount).label('total_volume')
    ).join(
        VirtualAccount, User.id == VirtualAccount.user_id
    ).join(
        VirtualAccountTransaction, VirtualAccount.id == VirtualAccountTransaction.virtual_account_id
    ).filter(
        VirtualAccountTransaction.status == TransactionStatus.COMPLETED
    ).group_by(
        User.id, User.first_name, User.last_name, User.username, User.role
    ).order_by(
        desc('total_volume')
    ).limit(10).all()
    
    top_users_list = [
        {
            "user_id": user.id,
            "name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
            "role": user.role.value,
            "transaction_count": user.transaction_count,
            "total_volume": float(user.total_volume)
        }
        for user in top_active_users
    ]
    
    return UserManagementSummary(
        total_users=total_users,
        insurance_companies=insurance_companies,
        brokers=brokers,
        new_users_this_month=new_users_this_month,
        active_users_today=active_users_today,
        users_with_virtual_accounts=users_with_virtual_accounts,
        top_active_users=top_users_list
    )


def create_system_alert(
    db: Session,
    alert_type: str,
    title: str,
    message: str,
    severity: str,
    related_transaction_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Create a system alert for admin monitoring.
    Note: This would typically write to a dedicated alerts table.
    For now, we'll return the alert data.
    """
    # In a real implementation, this would save to an alerts table
    return {
        "alert_type": alert_type,
        "title": title,
        "message": message,
        "severity": severity,
        "created_at": datetime.utcnow(),
        "resolved": False,
        "related_transaction_id": related_transaction_id,
        "metadata": metadata
    }


def get_recent_system_alerts(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent system alerts.
    Note: This would typically query a dedicated alerts table.
    For now, we'll return sample alerts based on recent failed transactions.
    """
    # Get recent failed transactions as alerts
    yesterday = datetime.now() - timedelta(days=1)
    failed_transactions = db.query(VirtualAccountTransaction).filter(
        and_(
            VirtualAccountTransaction.status == TransactionStatus.FAILED,
            VirtualAccountTransaction.created_at >= yesterday
        )
    ).order_by(desc(VirtualAccountTransaction.created_at)).limit(limit).all()
    
    alerts = []
    for i, tx in enumerate(failed_transactions):
        alerts.append({
            "id": i + 1,
            "alert_type": "ERROR",
            "title": "Transaction Failed",
            "message": f"Transaction {tx.transaction_reference} failed: {tx.remarks or 'Unknown error'}",
            "severity": "HIGH",
            "resolved": False,
            "created_at": tx.created_at,
            "related_transaction_id": tx.id
        })
    
    return alerts 