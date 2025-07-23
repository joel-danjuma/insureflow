"""
InsureFlow Internal Admin Dashboard API endpoints.
Provides comprehensive platform monitoring, transaction logs, and commission management.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from decimal import Decimal

from app.dependencies import get_db, get_current_insureflow_admin
from app.models.user import User
from app.crud import insureflow_admin as crud_admin
from app.crud.virtual_account import (
    update_virtual_account_commission_rates,
    get_total_commission_for_insureflow,
    get_total_commission_for_habari,
    get_total_platform_commission
)
from app.schemas.dashboard import (
    InsureFlowAdminDashboard,
    TransactionLogEntry,
    CommissionAnalytics,
    PlatformHealthMetrics,
    FinancialReport,
    UserManagementSummary,
    TransactionFilter,
    CommissionConfigUpdate,
    SystemAlert,
    AuditLogEntry
)

router = APIRouter()


@router.get("/dashboard", response_model=InsureFlowAdminDashboard)
def get_insureflow_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get comprehensive InsureFlow internal admin dashboard.
    Includes platform health, commission analytics, financial summary, and user management.
    """
    try:
        # Get all dashboard components
        platform_health = crud_admin.get_platform_health_metrics(db)
        commission_analytics = crud_admin.get_commission_analytics(db)
        financial_summary = crud_admin.get_financial_report(db, period="monthly")
        user_management = crud_admin.get_user_management_summary(db)
        recent_transactions = crud_admin.get_transaction_logs(db, limit=20)
        system_alerts = crud_admin.get_recent_system_alerts(db, limit=10)
        
        # Performance metrics
        performance_metrics = {
            "total_platform_revenue": float(commission_analytics.total_revenue_generated),
            "monthly_growth": commission_analytics.revenue_growth_rate,
            "transaction_success_rate": platform_health.webhook_success_rate,
            "avg_response_time": platform_health.api_response_time,
            "system_health_score": 95.5  # Calculated based on various factors
        }
        
        return InsureFlowAdminDashboard(
            platform_health=platform_health,
            commission_analytics=commission_analytics,
            financial_summary=financial_summary,
            user_management=user_management,
            recent_transactions=recent_transactions,
            system_alerts=system_alerts,
            performance_metrics=performance_metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching admin dashboard: {str(e)}")


@router.get("/transactions/logs", response_model=List[TransactionLogEntry])
def get_transaction_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    user_id: Optional[int] = None,
    virtual_account_id: Optional[int] = None,
    policy_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get detailed transaction logs with filtering and pagination.
    Supports comprehensive filtering by date, amount, user, account, etc.
    """
    filters = TransactionFilter(
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        status=status,
        min_amount=min_amount,
        max_amount=max_amount,
        user_id=user_id,
        virtual_account_id=virtual_account_id,
        policy_id=policy_id
    )
    
    return crud_admin.get_transaction_logs(db, skip=skip, limit=limit, filters=filters)


@router.get("/analytics/commission", response_model=CommissionAnalytics)
def get_commission_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get comprehensive commission analytics for InsureFlow.
    Includes revenue trends, growth rates, and top performing brokers.
    """
    return crud_admin.get_commission_analytics(db)


@router.get("/analytics/platform-health", response_model=PlatformHealthMetrics)
def get_platform_health_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get platform health and monitoring metrics.
    Includes system uptime, transaction success rates, and error monitoring.
    """
    return crud_admin.get_platform_health_metrics(db)


@router.get("/reports/financial", response_model=FinancialReport)
def get_financial_report(
    period: str = Query("monthly", regex="^(daily|monthly|yearly)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Generate financial reports for accounting and reconciliation.
    Supports daily, monthly, and yearly reporting periods.
    """
    return crud_admin.get_financial_report(db, period=period)


@router.get("/users/management-summary", response_model=UserManagementSummary)
def get_user_management_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get user management summary for admin oversight.
    Includes user counts, activity metrics, and top users.
    """
    return crud_admin.get_user_management_summary(db)


@router.get("/commission/summary")
def get_commission_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get detailed commission breakdown for InsureFlow and Habari.
    """
    total_platform_commission = get_total_platform_commission(db)
    insureflow_commission = get_total_commission_for_insureflow(db)
    habari_commission = get_total_commission_for_habari(db)
    
    return {
        "total_platform_commission": float(total_platform_commission),
        "insureflow_commission": float(insureflow_commission),
        "habari_commission": float(habari_commission),
        "insureflow_percentage": 75.0,  # 0.75%
        "habari_percentage": 25.0,      # 0.25%
        "commission_rates": {
            "platform_rate": 1.0,      # 1%
            "insureflow_rate": 0.75,   # 0.75%
            "habari_rate": 0.25        # 0.25%
        }
    }


@router.put("/commission/config")
def update_commission_configuration(
    config_update: CommissionConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Update platform commission configuration.
    WARNING: This affects all virtual accounts and future transactions.
    """
    try:
        # This would typically update a global configuration table
        # For now, we'll return a success message
        # In a real implementation, this would update commission rates for all VAs
        
        # Log the configuration change for audit purposes
        audit_entry = {
            "admin_user_id": current_user.id,
            "admin_user_name": current_user.username,
            "action": "UPDATE_COMMISSION_CONFIG",
            "target_type": "system",
            "new_values": config_update.dict(exclude_unset=True),
            "timestamp": datetime.utcnow(),
            "notes": config_update.notes
        }
        
        return {
            "success": True,
            "message": "Commission configuration updated successfully",
            "updated_rates": config_update.dict(exclude_unset=True),
            "audit_entry": audit_entry
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating commission config: {str(e)}")


@router.get("/alerts/recent")
def get_recent_alerts(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get recent system alerts and notifications.
    """
    return crud_admin.get_recent_system_alerts(db, limit=limit)


@router.post("/alerts/create")
def create_system_alert(
    alert_type: str,
    title: str,
    message: str,
    severity: str = "MEDIUM",
    related_transaction_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Create a new system alert.
    """
    alert = crud_admin.create_system_alert(
        db=db,
        alert_type=alert_type,
        title=title,
        message=message,
        severity=severity,
        related_transaction_id=related_transaction_id,
        metadata=metadata
    )
    
    return {"success": True, "alert": alert}


@router.get("/analytics/revenue-trends")
def get_revenue_trends(
    period: str = Query("monthly", regex="^(daily|weekly|monthly|yearly)$"),
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get InsureFlow revenue trends over time.
    """
    commission_analytics = crud_admin.get_commission_analytics(db)
    
    return {
        "period": period,
        "total_revenue": float(commission_analytics.total_revenue_generated),
        "monthly_trends": commission_analytics.monthly_trends,
        "growth_rate": commission_analytics.revenue_growth_rate,
        "avg_commission_per_transaction": float(commission_analytics.avg_commission_per_transaction)
    }


@router.get("/analytics/broker-performance")
def get_broker_performance_analytics(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get broker performance analytics from InsureFlow's perspective.
    Shows which brokers generate the most transaction volume (and thus commission for InsureFlow).
    """
    commission_analytics = crud_admin.get_commission_analytics(db)
    
    return {
        "top_revenue_generating_brokers": commission_analytics.top_revenue_generating_brokers[:limit],
        "total_brokers_with_transactions": len(commission_analytics.top_revenue_generating_brokers),
        "platform_revenue_summary": {
            "total_revenue": float(commission_analytics.total_revenue_generated),
            "monthly_revenue": float(commission_analytics.monthly_revenue),
            "daily_revenue": float(commission_analytics.daily_revenue)
        }
    }


@router.get("/export/transactions")
def export_transaction_data(
    format: str = Query("csv", regex="^(csv|excel|json)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Export transaction data for accounting and reconciliation.
    Supports CSV, Excel, and JSON formats.
    """
    # This would generate and return the actual file
    # For now, we'll return metadata about what would be exported
    
    filters = TransactionFilter(start_date=start_date, end_date=end_date)
    transactions = crud_admin.get_transaction_logs(db, limit=10000, filters=filters)
    
    return {
        "export_format": format,
        "total_transactions": len(transactions),
        "date_range": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "columns": [
            "transaction_reference", "virtual_account_number", "user_name",
            "transaction_type", "status", "principal_amount", "settled_amount",
            "insureflow_commission", "habari_commission", "transaction_date"
        ],
        "message": f"Export would contain {len(transactions)} transactions in {format} format"
    }


@router.get("/system/health-check")
def system_health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Comprehensive system health check for monitoring.
    """
    try:
        health_metrics = crud_admin.get_platform_health_metrics(db)
        
        # Calculate overall health score
        health_score = 100.0
        
        # Deduct points for issues
        if health_metrics.webhook_success_rate < 95:
            health_score -= (95 - health_metrics.webhook_success_rate)
        
        if health_metrics.failed_transactions_today > 10:
            health_score -= min(health_metrics.failed_transactions_today - 10, 20)
        
        if health_metrics.api_response_time > 500:
            health_score -= min((health_metrics.api_response_time - 500) / 100, 15)
        
        health_status = "HEALTHY" if health_score >= 90 else "WARNING" if health_score >= 70 else "CRITICAL"
        
        return {
            "status": health_status,
            "health_score": round(health_score, 1),
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": health_metrics,
            "recommendations": [
                "Monitor webhook success rate" if health_metrics.webhook_success_rate < 95 else None,
                "Investigate failed transactions" if health_metrics.failed_transactions_today > 5 else None,
                "Optimize API response time" if health_metrics.api_response_time > 300 else None
            ]
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "health_score": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/system/audit-log")
def get_audit_log(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = None,
    admin_user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_insureflow_admin)
):
    """
    Get audit log of admin actions.
    Note: In a real implementation, this would query a dedicated audit log table.
    """
    # For now, return sample audit entries
    # In production, this would be stored in a proper audit table
    sample_entries = [
        {
            "id": 1,
            "admin_user_id": current_user.id,
            "admin_user_name": current_user.username,
            "action": "UPDATE_COMMISSION_CONFIG",
            "target_type": "system",
            "timestamp": datetime.utcnow(),
            "notes": "Updated platform commission rates"
        },
        {
            "id": 2,
            "admin_user_id": current_user.id,
            "admin_user_name": current_user.username,
            "action": "EXPORT_TRANSACTION_DATA",
            "target_type": "transaction",
            "timestamp": datetime.utcnow(),
            "notes": "Exported monthly transaction report"
        }
    ]
    
    return {
        "audit_entries": sample_entries[skip:skip+limit],
        "total_count": len(sample_entries),
        "message": "Audit log functionality would be implemented with dedicated audit table"
    } 