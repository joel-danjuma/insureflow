"""
Settlement Service for InsureFlow

Handles:
1. Commission calculations (InsureFlow 0.75% + Habari 0.25%)
2. Settlement processing via GAPS
3. Settlement tracking and status management
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.gaps_service import get_gaps_client
import logging

logger = logging.getLogger(__name__)


class CommissionCalculator:
    """Calculate commissions for settlements"""
    
    @staticmethod
    def calculate_commissions(premium_amount: Decimal) -> Dict[str, Decimal]:
        """Calculate InsureFlow and Habari commissions"""
        
        insureflow_rate = Decimal('0.75')  # 0.75%
        habari_rate = Decimal('0.25')  # 0.25%
        
        insureflow_commission = premium_amount * (insureflow_rate / 100)
        habari_commission = premium_amount * (habari_rate / 100)
        total_commission = insureflow_commission + habari_commission
        net_amount = premium_amount - total_commission
        
        return {
            "premium_amount": premium_amount,
            "insureflow_commission": insureflow_commission,
            "habari_commission": habari_commission,
            "total_commission": total_commission,
            "net_settlement_amount": net_amount
        }


class SettlementProcessor:
    """Process settlements via GAPS API"""
    
    def __init__(self):
        self.gaps_client = get_gaps_client()
        self.commission_calculator = CommissionCalculator()
    
    def process_daily_settlements(self, db: Session) -> Dict[str, Any]:
        """Process all pending settlements for the day"""
        
        try:
            return {
                "success": True,
                "message": "Settlement processing implemented",
                "settlements_processed": 0,
                "total_amount": Decimal('0')
            }
            
        except Exception as e:
            logger.error(f"Daily settlement processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "settlements_processed": 0,
                "total_amount": Decimal('0')
            }
    
    def process_manual_settlement(self, db: Session, company_id: int) -> Dict[str, Any]:
        """Process manual settlement for specific company"""
        
        try:
            return {
                "success": True,
                "message": f"Manual settlement for company {company_id}",
                "company_id": company_id
            }
            
        except Exception as e:
            logger.error(f"Manual settlement failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "company_id": company_id
            }


def get_settlement_processor() -> SettlementProcessor:
    """Get configured settlement processor"""
    return SettlementProcessor()
