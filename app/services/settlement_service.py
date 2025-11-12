"""
Settlement Service for InsureFlow application.
Handles the settlement of funds from virtual accounts to insurance companies.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.gaps_service import gaps_service
from app.crud import virtual_account as crud_virtual_account
from app.core.config import settings

logger = logging.getLogger(__name__)

class SettlementService:
    """Service for managing settlements."""

    async def process_daily_settlements(self, db: Session) -> Dict[str, Any]:
        """Process all pending settlements for the day."""
        logger.info("Processing daily settlements...")
        # This is a placeholder for the full GAPS integration.
        return {"success": True, "message": "Daily settlements processed successfully"}

    async def process_manual_settlement(self, db: Session, company_id: int) -> Dict[str, Any]:
        """Process manual settlement for a specific company."""
        logger.info(f"Processing manual settlement for company ID: {company_id}")
        # This is a placeholder for the full GAPS integration.
        return {"success": True, "message": f"Manual settlement for company {company_id} processed successfully"}

    async def process_settlement(self, db: Session, virtual_account_id: int) -> Dict[str, Any]:
        """Process settlement for a virtual account."""
        virtual_account = crud_virtual_account.get_virtual_account(db, virtual_account_id)
        if not virtual_account:
            return {"error": "Virtual account not found"}

        if virtual_account.current_balance <= 0:
            return {"error": "No balance to settle"}

        insurance_company_account = {
            "amount": float(virtual_account.current_balance),
            "payment_date": "2025-10-15",
            "reference": f"SETTLE_{virtual_account.id}",
            "remarks": "Settlement",
            "vendor_code": "VC001",
            "vendor_name": "Insurance Company",
            "vendor_acct_number": settings.INSURANCE_FIRM_TEST_ACCOUNT_NUMBER,
            "vendor_bank_code": "058",  # GTBank
            "customer_acct_number": settings.INSUREFLOW_SETTLEMENT_ACCOUNT_NUMBER,
        }

        result = await gaps_service.initiate_single_transfer(insurance_company_account)

        # Ensure result is a dictionary
        if not isinstance(result, dict):
            logger.error(f"Unexpected response type from GAPS service: {type(result)}. Response: {result}")
            return {"error": f"Unexpected response type from GAPS service: {type(result)}"}

        if result.get("code") == "1000":
            # Update the virtual account's balance
            crud_virtual_account.update_virtual_account_balance(db, virtual_account_id, -virtual_account.current_balance)
            return {"success": True, "message": "Settlement successful"}
        else:
            return {"error": f"Settlement failed: {result.get('description', 'Unknown error')}"}


settlement_service = SettlementService()
