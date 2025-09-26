"""
Settlement Service for InsureFlow application.
Orchestrates the complete payment flow from Squad to GAPS.
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.virtual_account_transaction import VirtualAccountTransaction, TransactionStatus
from app.models.virtual_account import VirtualAccount
from app.models.policy import Policy
from app.services.gaps_service import gaps_service

logger = logging.getLogger(__name__)

class SettlementService:
    """Service for managing settlements from Squad to insurance firms via GAPS."""
    
    def __init__(self):
        self.insureflow_settlement_account = "1234567890"  # Configure this
        self.commission_rate = Decimal("0.01")  # 1% platform commission
    
    async def process_daily_settlements(self, db: Session) -> Dict[str, Any]:
        """
        Process daily settlements for all insurance firms.
        Called by scheduled task.
        """
        try:
            # Get all unsettled transactions from the last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            unsettled_transactions = db.query(VirtualAccountTransaction).filter(
                and_(
                    VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
                    VirtualAccountTransaction.transaction_date >= yesterday,
                    VirtualAccountTransaction.settlement_status == 'pending'
                )
            ).all()
            
            if not unsettled_transactions:
                logger.info("No unsettled transactions found")
                return {"success": True, "message": "No settlements to process"}
            
            # Group transactions by insurance firm
            settlements_by_firm = self._group_transactions_by_firm(db, unsettled_transactions)
            
            # Process settlements for each firm
            settlement_results = []
            
            for firm_id, transactions in settlements_by_firm.items():
                result = await self._process_firm_settlement(db, firm_id, transactions)
                settlement_results.append(result)
            
            return {
                "success": True,
                "settlements_processed": len(settlement_results),
                "results": settlement_results
            }
            
        except Exception as e:
            logger.error(f"Daily settlement processing failed: {str(e)}")
            return {"error": f"Settlement processing failed: {str(e)}"}
    
    def _group_transactions_by_firm(
        self,
        db: Session,
        transactions: List[VirtualAccountTransaction]
    ) -> Dict[int, List[VirtualAccountTransaction]]:
        """Group transactions by insurance firm."""
        firms = {}
        
        for transaction in transactions:
            # Get the virtual account and associated policy
            virtual_account = db.query(VirtualAccount).filter(
                VirtualAccount.id == transaction.virtual_account_id
            ).first()
            
            if virtual_account and virtual_account.policy:
                firm_id = virtual_account.policy.company_id
                
                if firm_id not in firms:
                    firms[firm_id] = []
                
                firms[firm_id].append(transaction)
        
        return firms
    
    async def _process_firm_settlement(
        self,
        db: Session,
        firm_id: int,
        transactions: List[VirtualAccountTransaction]
    ) -> Dict[str, Any]:
        """Process settlement for a specific insurance firm."""
        try:
            # Calculate total settlement amount (minus commission)
            total_amount = sum(t.settled_amount for t in transactions)
            commission_amount = total_amount * self.commission_rate
            net_settlement_amount = total_amount - commission_amount
            
            # Get firm details
            from app.models.company import InsuranceCompany
            firm = db.query(InsuranceCompany).filter(InsuranceCompany.id == firm_id).first()
            
            if not firm:
                return {"error": f"Insurance firm {firm_id} not found"}
            
            # Prepare settlement data for GAPS
            settlement_data = {
                "amount": net_settlement_amount,
                "beneficiary_account": firm.settlement_account or "1234567890",  # Default account
                "beneficiary_name": firm.name,
                "bank_code": getattr(firm, 'bank_code', None) or "058152052",  # Default to GTB
                "payment_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "reference": f"SETTLE_{firm_id}_{int(datetime.utcnow().timestamp())}",
                "remarks": f"Premium settlement for {len(transactions)} policies",
                "vendor_code": f"FIRM_{firm_id}"
            }
            
            # Process settlement via GAPS
            gaps_result = await gaps_service.process_bulk_settlement(
                [settlement_data],
                self.insureflow_settlement_account
            )
            
            if gaps_result.get("success"):
                # Update transaction settlement status
                for transaction in transactions:
                    transaction.settlement_status = 'settled'
                    transaction.settlement_date = datetime.utcnow()
                    transaction.settlement_reference = settlement_data["reference"]
                
                db.commit()
                
                logger.info(f"Settlement completed for firm {firm_id}: ₦{net_settlement_amount}")
                
                return {
                    "success": True,
                    "firm_id": firm_id,
                    "firm_name": firm.name,
                    "total_amount": float(total_amount),
                    "commission": float(commission_amount),
                    "net_settlement": float(net_settlement_amount),
                    "transactions_count": len(transactions),
                    "gaps_response": gaps_result
                }
            else:
                return {
                    "error": f"GAPS settlement failed for firm {firm_id}",
                    "gaps_error": gaps_result.get("error"),
                    "firm_name": firm.name
                }
                
        except Exception as e:
            logger.error(f"Firm settlement failed for firm {firm_id}: {str(e)}")
            return {"error": f"Settlement failed: {str(e)}"}
    
    async def process_manual_settlement(
        self,
        db: Session,
        firm_id: int,
        transaction_ids: List[int] = None
    ) -> Dict[str, Any]:
        """
        Process manual settlement for a specific firm.
        Used by admin interface.
        """
        try:
            # Get transactions to settle
            query = db.query(VirtualAccountTransaction).filter(
                VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
                VirtualAccountTransaction.settlement_status == 'pending'
            )
            
            if transaction_ids:
                query = query.filter(VirtualAccountTransaction.id.in_(transaction_ids))
            
            # Filter by firm through virtual account relationship
            transactions = []
            for transaction in query.all():
                virtual_account = db.query(VirtualAccount).filter(
                    VirtualAccount.id == transaction.virtual_account_id
                ).first()
                
                if virtual_account and virtual_account.policy and virtual_account.policy.company_id == firm_id:
                    transactions.append(transaction)
            
            if not transactions:
                return {"error": "No eligible transactions found for settlement"}
            
            # Process settlement
            result = await self._process_firm_settlement(db, firm_id, transactions)
            return result
            
        except Exception as e:
            logger.error(f"Manual settlement failed for firm {firm_id}: {str(e)}")
            return {"error": f"Manual settlement failed: {str(e)}"}
    
    def get_settlement_summary(self, db: Session, days: int = 7) -> Dict[str, Any]:
        """Get settlement summary for the last N days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get settled transactions
            settled_transactions = db.query(VirtualAccountTransaction).filter(
                and_(
                    VirtualAccountTransaction.settlement_status == 'settled',
                    VirtualAccountTransaction.settlement_date >= cutoff_date
                )
            ).all()
            
            # Get pending transactions
            pending_transactions = db.query(VirtualAccountTransaction).filter(
                and_(
                    VirtualAccountTransaction.status == TransactionStatus.COMPLETED,
                    VirtualAccountTransaction.settlement_status == 'pending',
                    VirtualAccountTransaction.transaction_date >= cutoff_date
                )
            ).all()
            
            # Calculate totals
            total_settled = sum(t.settled_amount for t in settled_transactions)
            total_pending = sum(t.settled_amount for t in pending_transactions)
            commission_earned = total_settled * self.commission_rate
            
            return {
                "success": True,
                "period_days": days,
                "settled_transactions": len(settled_transactions),
                "pending_transactions": len(pending_transactions),
                "total_settled_amount": float(total_settled),
                "total_pending_amount": float(total_pending),
                "commission_earned": float(commission_earned),
                "net_settled_amount": float(total_settled - commission_earned)
            }
            
        except Exception as e:
            logger.error(f"Failed to get settlement summary: {str(e)}")
            return {"error": f"Failed to get settlement summary: {str(e)}"}

# Global service instance
settlement_service = SettlementService()
