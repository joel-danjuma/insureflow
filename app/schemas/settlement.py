"""
Pydantic schemas for settlement operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime


class ManualSettlementRequest(BaseModel):
    """Request schema for manual settlement processing"""
    force: bool = Field(False, description="Force settlement even if below threshold")


class SettlementResponse(BaseModel):
    """Response schema for settlement operations"""
    success: bool
    message: str
    settlements_processed: int = 0
    total_amount: Decimal = Decimal('0')
    results: Optional[List[Dict[str, Any]]] = None


class SettlementSummary(BaseModel):
    """Settlement summary statistics"""
    success: bool
    period_days: int
    total_transactions: int = 0
    total_settlements: int = 0
    total_premium_amount: Decimal = Decimal('0')
    total_commission_earned: Decimal = Decimal('0')
    net_amount_settled: Decimal = Decimal('0')


class GAPSTestResponse(BaseModel):
    """Response schema for GAPS connection test"""
    connection_status: str = Field(..., description="SUCCESS, FAILED, or ERROR")
    gaps_response: Dict[str, Any]
    message: str


class CommissionBreakdown(BaseModel):
    """Commission calculation breakdown"""
    premium_amount: Decimal
    insureflow_commission: Decimal
    habari_commission: Decimal
    total_commission: Decimal
    net_settlement_amount: Decimal


class PendingSettlement(BaseModel):
    """Pending settlement details"""
    company_id: int
    company_name: str
    company_account: Optional[str] = None
    company_bank_code: Optional[str] = None
    transaction_count: int
    total_premium: Decimal
    total_commission: Decimal
    net_settlement: Decimal
    has_account_details: bool = Field(False, description="Whether company has settlement account configured")


class SettlementTransaction(BaseModel):
    """Individual settlement transaction"""
    transaction_id: int
    policy_id: int
    amount: Decimal
    commission_breakdown: CommissionBreakdown
    settlement_status: str
    settlement_date: Optional[datetime] = None
    settlement_reference: Optional[str] = None
    gaps_transaction_ref: Optional[str] = None
