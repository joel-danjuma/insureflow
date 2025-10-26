"""
Pydantic schemas for payment testing and simulation endpoints.
Used for stakeholder demonstrations and dashboard testing.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class TestVAAccountCreationRequest(BaseModel):
    """Payload for the direct VA creation test endpoint."""
    user_id: int = Field(..., description="The ID of the user to create the virtual account for.")


class TestVAFundingRequest(BaseModel):
    """Payload for the VA funding simulation endpoint."""
    virtual_account_number: str = Field(..., description="The virtual account number to fund.")
    amount: Decimal = Field(..., gt=0, description="The amount to fund in Naira.")


class TestVATransferRequest(BaseModel):
    """Payload for the VA to VA transfer test endpoint."""
    from_account: str = Field(..., description="The virtual account number to transfer from.")
    to_account: str = Field(..., description="The virtual account number to transfer to.")
    amount: Decimal = Field(..., gt=0, description="The amount to transfer in Naira.")


class TestingLogEntry(BaseModel):
    """Schema for individual log entries during testing."""
    timestamp: str
    message: str
    level: Literal["info", "success", "warning", "error"]
    data: Optional[Dict[str, Any]] = None


class SimulationSummary(BaseModel):
    """Summary statistics from payment flow simulation."""
    virtual_accounts_created: int = Field(..., description="Number of virtual accounts created")
    payments_simulated: int = Field(..., description="Number of payments simulated")
    settlements_triggered: int = Field(..., description="Number of settlements triggered")
    gaps_transfers: int = Field(..., description="Number of GAPS transfers executed")
    total_amount_processed: float = Field(..., description="Total amount processed in NGN")
    commission_calculated: float = Field(..., description="Total commission calculated in NGN")


class PaymentFlowSimulationRequest(BaseModel):
    """Request schema for payment flow simulation."""
    scenario: Literal["single", "bulk", "settlement"] = Field(
        default="single",
        description="Type of simulation scenario to run"
    )
    amount: Decimal = Field(
        default=Decimal('50000'),
        description="Amount to simulate for single payments (in NGN)"
    )
    virtual_account_count: int = Field(
        default=1,
        description="Number of virtual accounts to create for bulk scenarios"
    )


class PaymentFlowSimulationResponse(BaseModel):
    """Response schema for payment flow simulation."""
    success: bool
    logs: List[TestingLogEntry]
    summary: Optional[SimulationSummary] = None
    error: Optional[str] = None


class VirtualAccountCreationRequest(BaseModel):
    """Request schema for test virtual account creation."""
    user_identifier: Optional[str] = Field(
        default=None,
        description="Optional identifier for the test user"
    )
    company_id: Optional[int] = Field(
        default=None,
        description="Optional company ID to associate with the virtual account"
    )


class VirtualAccountCreationResponse(BaseModel):
    """Response schema for test virtual account creation."""
    success: bool
    virtual_account: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None


class PaymentSimulationRequest(BaseModel):
    """Request schema for direct payment simulation."""
    virtual_account_number: str = Field(..., description="Virtual account number to simulate payment to")
    amount: Decimal = Field(..., description="Amount to simulate (in NGN)")
    sender_name: Optional[str] = Field(default="Test Sender", description="Name of the payment sender")
    remarks: Optional[str] = Field(default="Test payment simulation", description="Payment remarks")


class PaymentSimulationResponse(BaseModel):
    """Response schema for direct payment simulation."""
    success: bool
    message: str
    transaction_reference: Optional[str] = None
    webhook_triggered: bool = False
    settlement_triggered: bool = False
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SettlementSimulationRequest(BaseModel):
    """Request schema for settlement simulation."""
    company_id: Optional[int] = Field(default=None, description="Specific company to simulate settlement for")
    force_settlement: bool = Field(default=False, description="Force settlement even if below threshold")
    settlement_type: Literal["manual", "automatic", "bulk"] = Field(
        default="automatic",
        description="Type of settlement to simulate"
    )


class SettlementSimulationResponse(BaseModel):
    """Response schema for settlement simulation."""
    success: bool
    settlement_reference: Optional[str] = None
    gaps_reference: Optional[str] = None
    amount_settled: Optional[float] = None
    commission_deducted: Optional[float] = None
    companies_processed: int = 0
    message: str
    logs: List[TestingLogEntry] = []
    error: Optional[str] = None


class GAPSTestRequest(BaseModel):
    """Request schema for GAPS API testing."""
    test_type: Literal["connection", "single_transfer", "bulk_transfer"] = Field(
        default="connection",
        description="Type of GAPS test to perform"
    )
    amount: Optional[Decimal] = Field(default=Decimal('1000'), description="Test amount for transfers")
    company_count: int = Field(default=1, description="Number of companies for bulk transfer test")


class GAPSTestResponse(BaseModel):
    """Response schema for GAPS API testing."""
    success: bool
    test_type: str
    gaps_response_code: Optional[str] = None
    gaps_message: Optional[str] = None
    transaction_reference: Optional[str] = None
    batch_reference: Optional[str] = None
    xml_request: Optional[str] = None
    xml_response: Optional[str] = None
    logs: List[TestingLogEntry] = []
    error: Optional[str] = None


class WebhookTestRequest(BaseModel):
    """Request schema for webhook testing."""
    webhook_type: Literal["payment", "virtual_account", "settlement"] = Field(
        default="payment",
        description="Type of webhook to simulate"
    )
    virtual_account_number: Optional[str] = None
    amount: Decimal = Field(default=Decimal('50000'), description="Amount for webhook simulation")
    transaction_reference: Optional[str] = None


class WebhookTestResponse(BaseModel):
    """Response schema for webhook testing."""
    success: bool
    webhook_processed: bool
    signature_valid: bool
    settlement_triggered: bool = False
    transaction_created: bool = False
    logs: List[TestingLogEntry] = []
    webhook_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ComprehensiveTestRequest(BaseModel):
    """Request schema for comprehensive end-to-end testing."""
    include_virtual_account_creation: bool = True
    include_payment_simulation: bool = True
    include_webhook_processing: bool = True
    include_settlement_testing: bool = True
    include_gaps_testing: bool = True
    test_scenarios: List[Literal["single", "bulk", "settlement", "error_handling"]] = ["single"]
    payment_amounts: List[Decimal] = [Decimal('50000')]


class ComprehensiveTestResponse(BaseModel):
    """Response schema for comprehensive end-to-end testing."""
    success: bool
    test_duration_seconds: float
    scenarios_completed: int
    total_logs: int
    summary: SimulationSummary
    detailed_results: Dict[str, Any]
    logs: List[TestingLogEntry]
    recommendations: List[str] = []
    error: Optional[str] = None


class TestingDashboardStats(BaseModel):
    """Statistics for the testing dashboard."""
    total_simulations_run: int = 0
    successful_simulations: int = 0
    failed_simulations: int = 0
    virtual_accounts_created: int = 0
    payments_simulated: int = 0
    settlements_processed: int = 0
    gaps_transfers_completed: int = 0
    total_amount_processed: float = 0.0
    last_simulation_time: Optional[datetime] = None
    average_simulation_duration: Optional[float] = None


class TestingDashboardResponse(BaseModel):
    """Response schema for testing dashboard data."""
    success: bool
    stats: TestingDashboardStats
    recent_logs: List[TestingLogEntry] = []
    active_simulations: int = 0
    system_status: Literal["healthy", "warning", "error"] = "healthy"
    recommendations: List[str] = []


class FullPaymentFlowTestResponse(BaseModel):
    """Response model for the end-to-end payment flow test."""
    success: bool
    message: str
    virtual_account_details: Dict[str, Any]
    payment_simulation_details: Dict[str, Any]
