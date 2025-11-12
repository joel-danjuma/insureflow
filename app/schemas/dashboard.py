"""
Pydantic schemas for dashboard data and analytics.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from decimal import Decimal


class DashboardKPIS(BaseModel):
    """Base KPI metrics for dashboard."""
    new_policies_this_month: int
    outstanding_premiums_total: float
    broker_count: int
    total_policies: int
    total_premium_collected: float
    average_policy_value: float
    policies_due_this_week: int
    overdue_payments: int
    conversion_rate: float


class DashboardData(BaseModel):
    """Legacy dashboard data structure for backward compatibility."""
    kpis: DashboardKPIS
    recent_policies: List[Dict[str, Any]]


class EnhancedDashboardKPIS(DashboardKPIS):
    """Extended KPIs with virtual account and commission data."""
    total_platform_commission: float  # Total 1% commission collected
    insureflow_commission_total: float  # 0.75% going to InsureFlow
    habari_commission_total: float  # 0.25% going to Habari
    virtual_accounts_count: int
    active_virtual_accounts: int
    total_virtual_account_balance: float
    pending_settlements: int
    top_performing_broker: Optional[str] = None
    monthly_growth_rate: float


class ChartDataPoint(BaseModel):
    """Data point for charts."""
    label: str
    value: float
    percentage: Optional[float] = None
    date: Optional[date] = None


class LineChartData(BaseModel):
    """Line chart data structure."""
    datasets: List[Dict[str, Any]]
    labels: List[str]


class PieChartData(BaseModel):
    """Pie chart data structure."""
    segments: List[ChartDataPoint]
    total: float


class PolicyTrend(BaseModel):
    """Policy trend data."""
    date: date
    count: int
    premium_amount: float


class TimeSeriesData(BaseModel):
    """Time series data for charts."""
    period: str
    data_points: List[ChartDataPoint]
    total: float
    growth_rate: float


class BarChartData(BaseModel):
    """Bar chart data structure."""
    labels: List[str]
    datasets: List[Dict[str, Any]]


class RecentPolicy(BaseModel):
    """Recent policy for dashboard display."""
    id: int
    policy_number: str
    policy_name: str
    policy_type: str
    company_name: str
    premium_amount: Decimal
    due_date: date
    status: str
    days_until_due: int


class BrokerPerformance(BaseModel):
    """Broker performance metrics."""
    broker_id: int
    broker_name: str
    policies_count: int
    total_premium: float
    conversion_rate: float
    last_policy_date: Optional[datetime] = None
    ranking: int


class VirtualAccountSummary(BaseModel):
    """Virtual account summary for dashboard."""
    account_id: int
    account_number: str
    account_type: str
    current_balance: float
    total_credits: float
    platform_commission_earned: float  # Total platform commission from this account
    last_transaction: Optional[datetime] = None
    status: str


class InsuranceFirmDashboard(BaseModel):
    """Dashboard data for insurance firm users."""
    kpis: EnhancedDashboardKPIS
    recent_policies: List[Dict[str, Any]]
    policy_trends: LineChartData
    broker_performance: List[BrokerPerformance]
    policy_distribution: PieChartData
    latest_payments: List[Dict[str, Any]] = []


class BrokerDashboard(BaseModel):
    """Dashboard data for broker users."""
    kpis: DashboardKPIS
    virtual_account_summary: List[VirtualAccountSummary]
    commission_trends: LineChartData
    individual_performance: BrokerPerformance


class AdminDashboard(BaseModel):
    """Dashboard data for admin users."""
    kpis: EnhancedDashboardKPIS
    system_health: Dict[str, Any]
    broker_performance: List[BrokerPerformance]
    virtual_account_summary: List[VirtualAccountSummary]
    commission_distribution: PieChartData


class CommissionSummary(BaseModel):
    """Schema for platform commission summary."""
    total_commission_pool: Decimal
    insureflow_commission: Decimal  # 0.75% of transactions
    habari_commission: Decimal      # 0.25% of transactions
    platform_commission_rate: Decimal
    insureflow_rate: Decimal
    habari_rate: Decimal


# InsureFlow Internal Admin Dashboard Schemas

class TransactionLogEntry(BaseModel):
    """Transaction log entry for admin monitoring."""
    id: int
    transaction_reference: str
    virtual_account_number: str
    user_name: str
    transaction_type: str
    transaction_indicator: str
    status: str
    principal_amount: Decimal
    settled_amount: Decimal
    fee_charged: Decimal
    total_platform_commission: Decimal
    insureflow_commission: Decimal
    habari_commission: Decimal
    currency: str
    sender_name: Optional[str] = None
    transaction_date: datetime
    webhook_received_at: Optional[datetime] = None
    policy_id: Optional[int] = None
    created_at: datetime


class CommissionAnalytics(BaseModel):
    """Commission analytics for InsureFlow admin."""
    total_revenue_generated: Decimal  # InsureFlow's 0.75% commission
    monthly_revenue: Decimal
    daily_revenue: Decimal
    revenue_growth_rate: float
    avg_commission_per_transaction: Decimal
    top_revenue_generating_brokers: List[Dict[str, Any]]
    monthly_trends: List[Dict[str, Any]]


class PlatformHealthMetrics(BaseModel):
    """Platform health and monitoring metrics."""
    total_active_users: int
    total_virtual_accounts: int
    active_virtual_accounts: int
    webhook_success_rate: float
    failed_transactions_today: int
    pending_settlements: int
    system_uptime: str
    api_response_time: float
    total_transaction_volume: Decimal
    processing_errors: List[Dict[str, Any]]


class FinancialReport(BaseModel):
    """Financial report for accounting and reconciliation."""
    report_period: str
    total_transactions: int
    gross_transaction_volume: Decimal
    total_fees_collected: Decimal
    insureflow_commission_earned: Decimal
    habari_commission_paid: Decimal
    net_revenue: Decimal
    pending_settlements: Decimal
    transaction_breakdown: Dict[str, Any]
    top_policies: List[Dict[str, Any]]


class UserManagementSummary(BaseModel):
    """User management summary for admin oversight."""
    total_users: int
    insurance_companies: int
    brokers: int
    new_users_this_month: int
    active_users_today: int
    users_with_virtual_accounts: int
    top_active_users: List[Dict[str, Any]]


class SupportTicketsSummary(BaseModel):
    """Summary of support tickets for admin dashboard."""
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int


class InsureFlowAdminDashboard(BaseModel):
    """Comprehensive InsureFlow internal admin dashboard."""
    platform_health: PlatformHealthMetrics
    commission_analytics: CommissionAnalytics
    financial_summary: FinancialReport
    user_management: UserManagementSummary
    recent_transactions: List[TransactionLogEntry]
    system_alerts: List[Dict[str, Any]]
    support_tickets_summary: Optional[SupportTicketsSummary] = None
    performance_metrics: Dict[str, Any]


class TransactionFilter(BaseModel):
    """Filter options for transaction logs."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    user_id: Optional[int] = None
    virtual_account_id: Optional[int] = None
    policy_id: Optional[int] = None


class CommissionConfigUpdate(BaseModel):
    """Schema for updating commission configuration."""
    platform_commission_rate: Optional[Decimal] = None
    insureflow_commission_rate: Optional[Decimal] = None
    habari_commission_rate: Optional[Decimal] = None
    notes: Optional[str] = None


class SystemAlert(BaseModel):
    """System alert for admin monitoring."""
    id: int
    alert_type: str  # 'ERROR', 'WARNING', 'INFO'
    title: str
    message: str
    severity: str
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    related_transaction_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditLogEntry(BaseModel):
    """Audit log entry for tracking admin actions."""
    id: int
    admin_user_id: int
    admin_user_name: str
    action: str
    target_type: str  # 'user', 'transaction', 'commission', 'system'
    target_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: str
    user_agent: str
    timestamp: datetime
    notes: Optional[str] = None 