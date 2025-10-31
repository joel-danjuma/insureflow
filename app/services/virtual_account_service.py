"""
Virtual Account Service for InsureFlow application.
Handles Squad Co virtual account operations and fund distribution.
"""
import logging
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import os
import requests
from fastapi import HTTPException

from app.core.config import settings
from app.models.virtual_account import VirtualAccount, VirtualAccountType, VirtualAccountStatus
from app.models.virtual_account_transaction import VirtualAccountTransaction, TransactionType, TransactionStatus, TransactionIndicator
from app.models.user import User
from app.crud import virtual_account as crud_virtual_account
from app.crud import policy as crud_policy
from app.models.policy import Policy
from app.services.settlement_service import settlement_service
from app.services.squad_co import squad_co_service
from app.schemas.virtual_account import SquadVirtualAccountCreatePayload

logger = logging.getLogger(__name__)


class VirtualAccountService:
    """Service for managing Squad Co virtual accounts."""
    
    def __init__(self):
        self.base_url = settings.SQUAD_BASE_URL
        self.secret_key = settings.SQUAD_SECRET_KEY
        
        if not self.secret_key or self.secret_key == "":
            logger.warning("Squad secret key not configured. Virtual account functionality will not work.")
        
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }
    
    async def create_individual_virtual_account(
        self, 
        db: Session,
        user: User,
        policy_id: Optional[int] = None,
        customer_identifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an individual virtual account for a user with comprehensive logging.
        """
        logger.info("🏦 CREATING INDIVIDUAL VIRTUAL ACCOUNT")
        logger.info(f"👤 User: {user.full_name} ({user.email})")
        logger.info(f"🆔 User ID: {user.id}")
        
        if not self.secret_key:
            logger.error("❌ Virtual account service not configured - missing secret key")
            return {"error": "Virtual account service not configured"}
        
        # Check if user already has a virtual account
        existing_va = crud_virtual_account.get_virtual_account_by_user(db, user_id=user.id)
        if existing_va:
            logger.info(f"✅ User already has virtual account: {existing_va.account_number}")
            return {
                "success": True,
                "virtual_account": {
                    "account_number": existing_va.account_number,
                    "account_name": existing_va.account_name,
                    "bank_name": existing_va.bank_name,
                    "status": existing_va.status.value
                }
            }
        
        # Generate customer identifier if not provided
        if not customer_identifier:
            customer_identifier = f"INSURE_USER_{user.id}_{int(datetime.now().timestamp())}"
        
        logger.info(f"🆔 Customer Identifier: {customer_identifier}")
        
        # Sanitize and validate phone number for Squad API
        mobile_number = "08000000000"  # Default valid number
        if user.phone_number:
            sanitized_number = "".join(filter(str.isdigit, user.phone_number))
            if len(sanitized_number) in [11, 13]:
                mobile_number = sanitized_number
            else:
                logger.warning(f"Invalid phone number format for user {user.id}: '{user.phone_number}'. Using default.")
        
        payload_data = {
            "customer_identifier": customer_identifier,
            "first_name": user.full_name.split()[0] if user.full_name else "User",
            "last_name": " ".join(user.full_name.split()[1:]) if len(user.full_name.split()) > 1 else "Customer",
            "mobile_num": mobile_number,
            "email": user.email,
            "beneficiary_account": "0123456789"  # Placeholder for testing
        }
        
        # Add optional fields if available
        # Use a hardcoded valid test BVN for sandbox environment to ensure successful VA creation
        if settings.SQUAD_BASE_URL and "sandbox" in settings.SQUAD_BASE_URL.lower():
            payload_data["bvn"] = "22222222222"
        elif user.bvn:
            payload_data["bvn"] = user.bvn
        
        if user.date_of_birth:
            payload_data["dob"] = user.date_of_birth.strftime("%m/%d/%Y")  # Correct format
        else:
            # Squad API requires DOB, provide a default for testing if not present
            payload_data["dob"] = "01/01/1990"
        if user.gender:
            payload_data["gender"] = "1" if user.gender.lower() in ["male", "m"] else "2"
        else:
            payload_data["gender"] = "1"  # Default to Male if not provided
        if user.address:
            payload_data["address"] = user.address
        else:
            # Squad API requires Address, provide a default for testing if not present
            payload_data["address"] = "123 Fictional Street, Lagos"
        
        # Create and validate the payload using the Pydantic schema
        squad_payload = SquadVirtualAccountCreatePayload(**payload_data)
        
        result = await squad_co_service.create_virtual_account(squad_payload)
        
        if result.get("error"):
            return result # Pass the error up
        
        if result.get("success"):
            # Save virtual account to database
            va_data = result.get("data", {})
            logger.info("✅ SQUAD CO VIRTUAL ACCOUNT CREATED SUCCESSFULLY")
            logger.info(f"🏦 Account Number: {va_data.get('virtual_account_number')}")
            logger.info(f"👤 Account Name: {va_data.get('first_name')} {va_data.get('last_name')}")
            logger.info(f"🏛️ Bank Code: {va_data.get('bank_code', '058')}")
            
            virtual_account = VirtualAccount(
                user_id=user.id,
                policy_id=policy_id,
                customer_identifier=customer_identifier,
                virtual_account_number=va_data.get("virtual_account_number"),
                bank_code=va_data.get("bank_code", "058"),
                account_type=VirtualAccountType.INDIVIDUAL.value,
                first_name=va_data.get("first_name"),
                last_name=va_data.get("last_name"),
                email=user.email,
                mobile_number=user.phone_number,
                squad_created_at=datetime.fromisoformat(va_data.get("created_at", "").replace("Z", "+00:00")) if va_data.get("created_at") else None,
                squad_updated_at=datetime.fromisoformat(va_data.get("updated_at", "").replace("Z", "+00:00")) if va_data.get("updated_at") else None,
            )
            
            logger.info("💾 SAVING VIRTUAL ACCOUNT TO DATABASE")
            db.add(virtual_account)
            db.commit()
            db.refresh(virtual_account)
            
            logger.info(f"✅ Virtual account saved to database with ID: {virtual_account.id}")
            logger.info(f"🎉 VIRTUAL ACCOUNT CREATION COMPLETED SUCCESSFULLY")
            
            return {
                "success": True, 
                "virtual_account": {
                    "account_number": virtual_account.virtual_account_number,
                    "account_name": f"{virtual_account.first_name} {virtual_account.last_name}",
                    "bank_name": "GTBank",  # Default bank name
                    "status": "active"
                }, 
                "squad_response": result
            }
        else:
            logger.error(f"❌ Squad API returned unsuccessful response: {result}")
            return {"error": f"Squad API error: {result.get('message', 'Unknown error')}"}
    
    async def create_business_virtual_account(
        self,
        db: Session,
        user: User,
        business_name: str,
        customer_identifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a business virtual account for a user.
        """
        if not self.secret_key:
            return {"error": "Virtual account service not configured"}
        
        # Generate customer identifier if not provided
        if not customer_identifier:
            customer_identifier = f"INSURE_BIZ_{user.id}_{int(datetime.now().timestamp())}"
        
        payload_data = {
            "customer_identifier": customer_identifier,
            "business_name": business_name,
            "mobile_num": user.phone_number or "08000000000",
            "email": user.email,
            "beneficiary_account": "0123456789"  # Beneficiary account for business not specified, using placeholder
        }
        
        # Add BVN if available
        if user.bvn:
            payload_data["bvn"] = user.bvn
        
        logger.info(f"Creating business virtual account for user {user.id}: {business_name}")
        
        # This part needs adjustment, as the schema is for individual accounts.
        # For now, we will manually construct the dictionary for business accounts,
        # as it has a different structure ('business_name' instead of 'first_name'/'last_name').
        # A separate schema for business accounts could be created in the future.
        
        result = await squad_co_service.create_virtual_account(payload_data)

        if result.get("error"):
            return result

        if result.get("success"):
            # Save virtual account to database
            va_data = result.get("data", {})
            virtual_account = VirtualAccount(
                user_id=user.id,
                customer_identifier=customer_identifier,
                virtual_account_number=va_data.get("virtual_account_number"),
                bank_code=va_data.get("bank_code", "058"),
                account_type=VirtualAccountType.BUSINESS.value,
                business_name=business_name,
                first_name=va_data.get("first_name"),  # Squad returns business name split
                last_name=va_data.get("last_name"),
                email=user.email,
                mobile_number=user.phone_number,
                squad_created_at=datetime.fromisoformat(va_data.get("created_at", "").replace("Z", "+00:00")) if va_data.get("created_at") else None,
                squad_updated_at=datetime.fromisoformat(va_data.get("updated_at", "").replace("Z", "+00:00")) if va_data.get("updated_at") else None,
            )
            
            db.add(virtual_account)
            db.commit()
            db.refresh(virtual_account)
            
            logger.info(f"Business virtual account created successfully: {virtual_account.virtual_account_number}")
            return {"success": True, "virtual_account": virtual_account, "squad_response": result}
        else:
            logger.error(f"Squad API returned unsuccessful response: {result}")
            return {"error": f"Squad API error: {result.get('message', 'Unknown error')}"}
    
    async def simulate_payment(
        self,
        virtual_account_number: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Simulate a payment to a virtual account using the Squad Co service.
        """
        return await squad_co_service.simulate_payment(virtual_account_number, amount)
    
    async def process_webhook_transaction(
        self,
        db: Session,
        webhook_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process incoming webhook transaction from Squad Co.
        Handles fund distribution and commission calculation.
        """
        try:
            transaction_ref = webhook_data.get("transaction_reference")
            virtual_account_number = webhook_data.get("virtual_account_number")
            principal_amount = Decimal(webhook_data.get("principal_amount", "0"))
            settled_amount = Decimal(webhook_data.get("settled_amount", "0"))
            fee_charged = Decimal(webhook_data.get("fee_charged", "0"))
            
            # Enhanced logging for stakeholder visibility
            logger.info(f"🔔 WEBHOOK RECEIVED: Virtual Account {virtual_account_number}")
            logger.info(f"💰 PAYMENT AMOUNT: ₦{principal_amount:,} (settled: ₦{settled_amount:,})")
            logger.info(f"📊 TRANSACTION REF: {transaction_ref}")
            
            # Find the virtual account
            virtual_account = crud_virtual_account.get_virtual_account_by_number(
                db, virtual_account_number=virtual_account_number
            )
            
            if not virtual_account:
                logger.error(f"❌ VIRTUAL ACCOUNT NOT FOUND: {virtual_account_number}")
                return {"error": "Virtual account not found"}
            
            logger.info(f"✅ VIRTUAL ACCOUNT FOUND: {virtual_account.account_name}")
            
            # Find the associated policy using the virtual account
            policy = db.query(Policy).filter(Policy.id == virtual_account.policy_id).first()
            if not policy:
                logger.error(f"❌ POLICY NOT FOUND FOR VIRTUAL ACCOUNT: {virtual_account.id}")
                # Even if no policy is found, we should still process the transaction
                # but we cannot update a policy status.
            else:
                # Verify the amount against the policy's premium
                if settled_amount < policy.premium_amount:
                    logger.warning(f"⚠️ PAYMENT AMOUNT MISMATCH: Received {settled_amount}, expected {policy.premium_amount}. Treating as underpayment.")
                    policy.payment_status = "partial_payment" 
                else:
                    if settled_amount > policy.premium_amount:
                        logger.warning(f"⚠️ PAYMENT AMOUNT MISMATCH: Received {settled_amount}, expected {policy.premium_amount}. Treating as overpayment.")
                    # Mark the policy as paid
                    policy.payment_status = "paid"
            
            # Calculate platform commission split
            total_platform_commission = settled_amount * virtual_account.platform_commission_rate
            insureflow_commission = settled_amount * virtual_account.insureflow_commission_rate
            habari_commission = settled_amount * virtual_account.habari_commission_rate
            
            # Enhanced logging for commission calculations
            logger.info(f"💼 COMMISSION CALCULATION:")
            logger.info(f"   - Total Platform Commission: ₦{total_platform_commission:,}")
            logger.info(f"   - InsureFlow Commission (0.75%): ₦{insureflow_commission:,}")
            logger.info(f"   - Habari Commission (0.25%): ₦{habari_commission:,}")
            logger.info(f"   - Net Settlement Amount: ₦{(settled_amount - total_platform_commission):,}")
            
            # Create transaction record
            transaction = VirtualAccountTransaction(
                virtual_account_id=virtual_account.id,
                transaction_reference=transaction_ref,
                squad_transaction_reference=transaction_ref,
                transaction_type=TransactionType.CREDIT,
                transaction_indicator=TransactionIndicator.C,
                status=TransactionStatus.COMPLETED,
                principal_amount=principal_amount,
                settled_amount=settled_amount,
                fee_charged=fee_charged,
                total_platform_commission=total_platform_commission,
                insureflow_commission=insureflow_commission,
                habari_commission=habari_commission,
                currency=webhook_data.get("currency", "NGN"),
                sender_name=webhook_data.get("sender_name"),
                remarks=webhook_data.get("remarks"),
                transaction_date=datetime.fromisoformat(
                    webhook_data.get("transaction_date", "").replace("+01:00", "+00:00")
                ) if webhook_data.get("transaction_date") else datetime.utcnow(),
                webhook_received_at=datetime.utcnow(),
                transaction_metadata=json.dumps(webhook_data)
            )
            
            db.add(transaction)
            
            # Update virtual account balances
            virtual_account.total_credits += settled_amount
            virtual_account.current_balance += settled_amount
            virtual_account.last_activity_at = datetime.utcnow()
            
            db.commit()
            
            # Check if auto-settlement is enabled and threshold is met
            logger.info(f"🎯 SETTLEMENT CHECK:")
            logger.info(f"   - Current Balance: ₦{virtual_account.current_balance:,}")
            logger.info(f"   - Settlement Threshold: ₦{virtual_account.settlement_threshold:,}")
            logger.info(f"   - Auto-Settlement Enabled: {virtual_account.auto_settlement}")
            
            if virtual_account.auto_settlement and virtual_account.current_balance >= virtual_account.settlement_threshold:
                logger.info(f"🚀 SETTLEMENT TRIGGERED: Threshold exceeded, initiating auto-settlement")
                await settlement_service.process_settlement(db, virtual_account.id)
            else:
                logger.info(f"⏳ SETTLEMENT NOT TRIGGERED: Threshold not met or auto-settlement disabled")
            
            logger.info(f"✅ WEBHOOK PROCESSING COMPLETE: {transaction_ref}")
            return {"success": True, "transaction": transaction}
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing webhook transaction: {str(e)}")
            return {"error": f"Error processing transaction: {str(e)}"}
    
    async def get_customer_transactions(
        self,
        customer_identifier: str
    ) -> Dict[str, Any]:
        """
        Get all transactions for a customer from Squad Co.
        """
        if not self.secret_key:
            return {"error": "Virtual account service not configured"}
        
        url = f"{self.base_url}/virtual-account/customer/transactions/{customer_identifier}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Retrieved transactions for customer {customer_identifier}")
                return result
                
            except httpx.HTTPStatusError as e:
                error_detail = self._extract_error_message(e.response)
                logger.error(f"Squad API HTTP error: {error_detail}")
                return {"error": f"Squad API error: {error_detail}"}
                
            except Exception as e:
                logger.error(f"Unexpected error retrieving customer transactions: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}
    
    def _initiate_auto_settlement(self, db: Session, virtual_account: VirtualAccount):
        """
        Initiate automatic settlement for a virtual account.
        This triggers the settlement service to process GAPS bulk transfer.
        """
        try:
            from app.services.settlement_service import get_settlement_processor
            
            # Calculate net amount after platform commission
            net_amount = virtual_account.net_amount_after_commission
            
            logger.info(f"Auto-settlement initiated for VA {virtual_account.virtual_account_number}: ₦{net_amount}")
            logger.info(f"Platform commission: ₦{virtual_account.total_platform_commission} (InsureFlow: ₦{virtual_account.insureflow_commission_amount}, Habari: ₦{virtual_account.habari_commission_amount})")
            
            # Get the insurance company for this virtual account
            from app.models.company import InsuranceCompany
            company = db.query(InsuranceCompany).filter(
                InsuranceCompany.id == virtual_account.company_id
            ).first()
            
            if not company:
                logger.error(f"No company found for virtual account {virtual_account.virtual_account_number}")
                return
            
            if not company.settlement_account_number:
                logger.warning(f"No settlement account configured for {company.name} - creating pending settlement record")
                
                # Create pending settlement transaction record
                settlement_transaction = VirtualAccountTransaction(
                    virtual_account_id=virtual_account.id,
                    transaction_reference=f"SETTLE_{virtual_account.id}_{int(datetime.now().timestamp())}",
                    transaction_type=TransactionType.SETTLEMENT,
                    transaction_indicator=TransactionIndicator.D,
                    status=TransactionStatus.PENDING,
                    principal_amount=net_amount,
                    settled_amount=net_amount,
                    transaction_date=datetime.utcnow(),
                    remarks=f"Auto-settlement pending - no settlement account for {company.name}"
                )
                
                db.add(settlement_transaction)
                db.commit()
                return
            
            # Process settlement via settlement service
            settlement_processor = get_settlement_processor()
            
            logger.info(f"Processing auto-settlement via GAPS for company: {company.name}")
            
            # Use manual settlement for individual virtual account
            result = settlement_processor.process_manual_settlement(db, company.id)
            
            if result.get("success"):
                logger.info(f"Auto-settlement completed successfully: {result.get('message')}")
                logger.info(f"GAPS Reference: {result.get('gaps_transaction_reference', 'N/A')}")
            else:
                logger.error(f"Auto-settlement failed: {result.get('error')}")
                
                # Create failed settlement transaction record
                settlement_transaction = VirtualAccountTransaction(
                    virtual_account_id=virtual_account.id,
                    transaction_reference=f"SETTLE-FAIL_{virtual_account.id}_{int(datetime.now().timestamp())}",
                    transaction_type=TransactionType.SETTLEMENT,
                    transaction_indicator=TransactionIndicator.D,
                    status=TransactionStatus.FAILED,
                    principal_amount=net_amount,
                    settled_amount=Decimal('0'),
                    transaction_date=datetime.utcnow(),
                    remarks=f"Auto-settlement failed: {result.get('error', 'Unknown error')}"
                )
                
                db.add(settlement_transaction)
                db.commit()
            
        except Exception as e:
            logger.error(f"Error initiating auto-settlement: {str(e)}")
            db.rollback()
    
    def _extract_error_message(self, response) -> str:
        """Extract error message from Squad API response."""
        try:
            error_data = response.json()
            if 'message' in error_data:
                return error_data['message']
            elif 'errors' in error_data:
                return str(error_data['errors'])
            else:
                return response.text
        except:
            return response.text


# Global service instance
virtual_account_service = VirtualAccountService() 

async def simulate_policy_payment(policy_id: int, db, user):
    # Fetch the policy and its virtual account
    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    va = db.query(models.VirtualAccount).filter(models.VirtualAccount.policy_id == policy_id).first()
    if not va:
        raise HTTPException(status_code=404, detail="Virtual account not found for policy")
    squad_secret = os.getenv("SQUAD_SECRET_KEY")
    if not squad_secret:
        raise HTTPException(status_code=500, detail="Squad secret key not configured")
    url = "https://sandbox-api-d.squadco.com/virtual-account/simulate/payment"
    payload = {
        "virtual_account_number": va.virtual_account_number,
        "amount": str(policy.premium_amount),
        "dva": True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {squad_secret}"
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Optionally log the simulation
        # ...
        return {"success": data.get("success"), "message": data.get("message"), "data": data.get("data")}
    except Exception as e:
        # Optionally log the error
        raise HTTPException(status_code=500, detail=f"Squad simulation failed: {str(e)}") 