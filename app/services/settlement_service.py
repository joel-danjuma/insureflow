"""
Settlement Service for InsureFlow application.
Handles the settlement of funds from virtual accounts to insurance companies.
"""
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.gaps_service import gaps_service
from app.crud import virtual_account as crud_virtual_account

logger = logging.getLogger(__name__)


class SettlementService:
    """Service for managing settlements."""

    async def process_settlement(self, db: Session, virtual_account_id: int) -> Dict[str, Any]:
        """Process settlement for a virtual account."""
        virtual_account = crud_virtual_account.get_virtual_account(db, virtual_account_id)
        if not virtual_account:
            return {"error": "Virtual account not found"}

        if virtual_account.current_balance <= 0:
            return {"error": "No balance to settle"}

        # In a real-world scenario, you would fetch the insurance company's
        # bank account details from the database.
        # For this example, we'll use dummy data.
        insurance_company_account = {
            "amount": float(virtual_account.current_balance),
            "payment_date": "2025-10-15",
            "reference": f"SETTLE_{virtual_account.id}",
            "remarks": "Settlement",
            "vendor_code": "VC001",
            "vendor_name": "Insurance Company",
            "vendor_acct_number": "0123456789",
            "vendor_bank_code": "058",  # GTBank
            "customer_acct_number": "9876543210",  # InsureFlow's account
        }

        result = await gaps_service.initiate_single_transfer(insurance_company_account)

        if result.get("code") == "1000":
            # Update the virtual account's balance
            crud_virtual_account.update_virtual_account_balance(db, virtual_account_id, -virtual_account.current_balance)
            return {"success": True, "message": "Settlement successful"}
        else:
            return {"error": f"Settlement failed: {result.get('description')}"}


settlement_service = SettlementService()
