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
        """Process all pending settlements for the day with comprehensive logging"""
        
        logger.info("💰 STARTING DAILY SETTLEMENT PROCESS")
        
        try:
            from app.crud.virtual_account import get_virtual_accounts_for_settlement
            from app.models.company import InsuranceCompany
            from app.core.config import settings
            
            # Get virtual accounts ready for settlement
            logger.info("📊 FETCHING SETTLEMENT-READY VIRTUAL ACCOUNTS")
            virtual_accounts = get_virtual_accounts_for_settlement(db)
            
            if not virtual_accounts:
                logger.info("ℹ️ No virtual accounts ready for settlement")
                return {
                    "success": True,
                    "message": "No virtual accounts ready for settlement",
                    "settlements_processed": 0,
                    "total_amount": Decimal('0')
                }
            
            logger.info(f"📋 Found {len(virtual_accounts)} virtual accounts ready for settlement")
            
            # Group settlements by insurance company
            logger.info("🏢 GROUPING SETTLEMENTS BY INSURANCE COMPANY")
            company_settlements = {}
            total_settlement_amount = Decimal('0')
            
            for va in virtual_accounts:
                # Get the insurance company for this virtual account
                company = db.query(InsuranceCompany).filter(
                    InsuranceCompany.id == va.company_id
                ).first()
                
                if not company or not company.settlement_account_number:
                    logger.warning(f"⚠️ Skipping VA {va.account_number} - no settlement account for company")
                    continue
                
                # Calculate net settlement amount (after platform commission)
                net_amount = va.net_amount_after_commission
                
                if net_amount <= 0:
                    logger.warning(f"⚠️ Skipping VA {va.account_number} - net amount is {net_amount}")
                    continue
                
                company_id = company.id
                if company_id not in company_settlements:
                    company_settlements[company_id] = {
                        "company": company,
                        "total_amount": Decimal('0'),
                        "virtual_accounts": []
                    }
                
                company_settlements[company_id]["total_amount"] += net_amount
                company_settlements[company_id]["virtual_accounts"].append(va)
                total_settlement_amount += net_amount
                
                logger.info(f"✅ VA {va.account_number}: ₦{net_amount:,.2f} → {company.name}")
            
            logger.info(f"💰 SETTLEMENT SUMMARY:")
            logger.info(f"   - Total Amount to Companies: ₦{total_settlement_amount:,.2f}")
            logger.info(f"   - Companies: {len(company_settlements)}")
            logger.info(f"   - Virtual Accounts: {len(virtual_accounts)}")
            
            if not company_settlements:
                return {
                    "success": True,
                    "message": "No settlements to process (no valid company accounts)",
                    "settlements_processed": 0,
                    "total_amount": Decimal('0')
                }
            
            # Prepare bulk transfers for GAPS
            logger.info("🏦 PREPARING GAPS BULK TRANSFERS")
            transfers = []
            for company_id, settlement_data in company_settlements.items():
                company = settlement_data["company"]
                amount = settlement_data["total_amount"]
                
                transfer = {
                    "amount": amount,
                    "vendor_account": company.settlement_account_number,
                    "vendor_bank_code": company.settlement_bank_code,
                    "vendor_name": company.settlement_account_name or company.name,
                    "vendor_code": f"INS{company.id:03d}",
                    "customer_account": settings.INSUREFLOW_SETTLEMENT_ACCOUNT or "1234567890",
                    "reference": f"DAILY-SETTLE-{datetime.now().strftime('%Y%m%d')}-{company.id}",
                    "remarks": f"Daily settlement for {company.name}",
                    "payment_date": datetime.now().date()
                }
                
                transfers.append(transfer)
                logger.info(f"✅ Prepared settlement: {company.name} → ₦{amount:,.2f}")
                logger.info(f"   - Account: {company.settlement_account_number}")
                logger.info(f"   - Bank: {company.settlement_bank_code}")
                logger.info(f"   - Reference: {transfer['reference']}")
            
            # Execute bulk transfer via GAPS
            logger.info("📞 CALLING GAPS API FOR BULK TRANSFER")
            logger.info(f"📊 Transfer Details:")
            logger.info(f"   - Companies: {len(transfers)}")
            logger.info(f"   - Total Amount: ₦{total_settlement_amount:,.2f}")
            
            gaps_result = self.gaps_client.bulk_transfer(transfers)
            
            if gaps_result.get("success"):
                logger.info("✅ GAPS BULK TRANSFER SUCCESSFUL")
                logger.info(f"📝 GAPS Batch Reference: {gaps_result.get('batch_reference', 'N/A')}")
                logger.info(f"💰 Total Transferred: ₦{gaps_result.get('total_amount', total_settlement_amount):,.2f}")
                
                # Update virtual account balances and create settlement records
                logger.info("💾 UPDATING VIRTUAL ACCOUNT BALANCES AND CREATING SETTLEMENT RECORDS")
                settlements_processed = 0
                
                for company_id, settlement_data in company_settlements.items():
                    for va in settlement_data["virtual_accounts"]:
                        # Create settlement transaction record
                        from app.models.virtual_account import VirtualAccountTransaction, TransactionType, TransactionIndicator, TransactionStatus
                        
                        settlement_transaction = VirtualAccountTransaction(
                            virtual_account_id=va.id,
                            transaction_reference=f"SETTLE_{va.id}_{int(datetime.now().timestamp())}",
                            transaction_type=TransactionType.SETTLEMENT,
                            transaction_indicator=TransactionIndicator.D,
                            status=TransactionStatus.COMPLETED,
                            principal_amount=va.net_amount_after_commission,
                            settled_amount=va.net_amount_after_commission,
                            transaction_date=datetime.utcnow(),
                            remarks=f"Daily settlement via GAPS - Batch: {gaps_result.get('batch_reference', 'N/A')}"
                        )
                        
                        db.add(settlement_transaction)
                        
                        # Reset virtual account balance
                        va.current_balance = Decimal('0')
                        va.last_settlement_at = datetime.utcnow()
                        
                        logger.info(f"✅ Settlement record created for VA {va.account_number}: ₦{va.net_amount_after_commission:,.2f}")
                        
                        settlements_processed += 1
                
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Daily settlements processed successfully via GAPS",
                    "settlements_processed": settlements_processed,
                    "total_amount": total_settlement_amount,
                    "gaps_batch_reference": gaps_result.get("batch_reference"),
                    "gaps_response_code": gaps_result.get("response_code")
                }
            else:
                logger.error(f"GAPS bulk transfer failed: {gaps_result}")
                return {
                    "success": False,
                    "error": f"GAPS transfer failed: {gaps_result.get('error', 'Unknown error')}",
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
            from app.models.company import InsuranceCompany
            from app.models.virtual_account import VirtualAccount
            from app.core.config import settings
            
            # Get the company
            company = db.query(InsuranceCompany).filter(
                InsuranceCompany.id == company_id
            ).first()
            
            if not company:
                return {
                    "success": False,
                    "error": f"Company with ID {company_id} not found",
                    "company_id": company_id
                }
            
            if not company.settlement_account_number:
                return {
                    "success": False,
                    "error": f"No settlement account configured for {company.name}",
                    "company_id": company_id
                }
            
            # Get virtual accounts for this company with balance above threshold
            virtual_accounts = db.query(VirtualAccount).filter(
                VirtualAccount.company_id == company_id,
                VirtualAccount.current_balance > VirtualAccount.settlement_threshold,
                VirtualAccount.status == "ACTIVE"
            ).all()
            
            if not virtual_accounts:
                return {
                    "success": False,
                    "error": f"No virtual accounts ready for settlement for {company.name}",
                    "company_id": company_id
                }
            
            # Calculate total settlement amount
            total_amount = sum(va.net_amount_after_commission for va in virtual_accounts)
            
            if total_amount <= 0:
                return {
                    "success": False,
                    "error": f"No settlement amount available for {company.name}",
                    "company_id": company_id
                }
            
            # Prepare single transfer for GAPS
            transfer = {
                "amount": total_amount,
                "vendor_account": company.settlement_account_number,
                "vendor_bank_code": company.settlement_bank_code,
                "vendor_name": company.settlement_account_name or company.name,
                "vendor_code": f"INS{company.id:03d}",
                "customer_account": settings.INSUREFLOW_SETTLEMENT_ACCOUNT or "1234567890",
                "reference": f"MANUAL-SETTLE-{datetime.now().strftime('%Y%m%d%H%M')}-{company.id}",
                "remarks": f"Manual settlement for {company.name}",
                "payment_date": datetime.now().date()
            }
            
            logger.info(f"Processing manual settlement: {company.name} → ₦{total_amount:,}")
            
            # Execute single transfer via GAPS
            gaps_result = self.gaps_client.single_transfer(transfer)
            
            if gaps_result.get("success"):
                # Update virtual account balances and create settlement records
                settlements_processed = 0
                
                for va in virtual_accounts:
                    # Create settlement transaction record
                    from app.models.virtual_account import VirtualAccountTransaction, TransactionType, TransactionIndicator, TransactionStatus
                    
                    settlement_transaction = VirtualAccountTransaction(
                        virtual_account_id=va.id,
                        transaction_reference=f"MANUAL-SETTLE_{va.id}_{int(datetime.now().timestamp())}",
                        transaction_type=TransactionType.SETTLEMENT,
                        transaction_indicator=TransactionIndicator.D,
                        status=TransactionStatus.COMPLETED,
                        principal_amount=va.net_amount_after_commission,
                        settled_amount=va.net_amount_after_commission,
                        transaction_date=datetime.utcnow(),
                        remarks=f"Manual settlement via GAPS - Ref: {gaps_result.get('transaction_reference', 'N/A')}"
                    )
                    
                    db.add(settlement_transaction)
                    
                    # Reset virtual account balance
                    va.current_balance = Decimal('0')
                    va.last_settlement_at = datetime.utcnow()
                    
                    settlements_processed += 1
                
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Manual settlement processed successfully for {company.name}",
                    "company_id": company_id,
                    "settlements_processed": settlements_processed,
                    "total_amount": total_amount,
                    "gaps_transaction_reference": gaps_result.get("transaction_reference"),
                    "gaps_response_code": gaps_result.get("response_code")
                }
            else:
                logger.error(f"GAPS single transfer failed: {gaps_result}")
                return {
                    "success": False,
                    "error": f"GAPS transfer failed: {gaps_result.get('error', 'Unknown error')}",
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
