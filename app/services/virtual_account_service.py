"""
Virtual Account Service for InsureFlow application.
Handles Squad Co virtual account operations and fund distribution.
"""
import httpx
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
        customer_identifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an individual virtual account for a user.
        """
        if not self.secret_key:
            return {"error": "Virtual account service not configured"}
        
        # Generate customer identifier if not provided
        if not customer_identifier:
            customer_identifier = f"INSURE_USER_{user.id}_{int(datetime.now().timestamp())}"
        
        url = f"{self.base_url}/virtual-account"
        
        payload = {
            "customer_identifier": customer_identifier,
            "first_name": user.full_name.split()[0] if user.full_name else "User",
            "last_name": " ".join(user.full_name.split()[1:]) if len(user.full_name.split()) > 1 else "Customer",
            "mobile_num": user.phone_number or "08000000000",
            "email": user.email,
        }
        
        # Add optional fields if available
        if user.bvn:
            payload["bvn"] = user.bvn
        if user.date_of_birth:
            payload["dob"] = user.date_of_birth.strftime("%d/%m/%Y")
        if user.gender:
            payload["gender"] = "1" if user.gender.lower() in ["male", "m"] else "2"
        if user.address:
            payload["address"] = user.address
        
        logger.info(f"Creating individual virtual account for user {user.id}: {customer_identifier}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("success"):
                    # Save virtual account to database
                    va_data = result.get("data", {})
                    virtual_account = VirtualAccount(
                        user_id=user.id,
                        customer_identifier=customer_identifier,
                        virtual_account_number=va_data.get("virtual_account_number"),
                        bank_code=va_data.get("bank_code", "058"),
                        account_type=VirtualAccountType.INDIVIDUAL,
                        first_name=va_data.get("first_name"),
                        last_name=va_data.get("last_name"),
                        email=user.email,
                        mobile_number=user.phone_number,
                        squad_created_at=datetime.fromisoformat(va_data.get("created_at", "").replace("Z", "+00:00")) if va_data.get("created_at") else None,
                        squad_updated_at=datetime.fromisoformat(va_data.get("updated_at", "").replace("Z", "+00:00")) if va_data.get("updated_at") else None,
                    )
                    
                    db.add(virtual_account)
                    db.commit()
                    db.refresh(virtual_account)
                    
                    logger.info(f"Individual virtual account created successfully: {virtual_account.virtual_account_number}")
                    return {"success": True, "virtual_account": virtual_account, "squad_response": result}
                else:
                    logger.error(f"Squad API returned unsuccessful response: {result}")
                    return {"error": f"Squad API error: {result.get('message', 'Unknown error')}"}
                
            except httpx.HTTPStatusError as e:
                error_detail = self._extract_error_message(e.response)
                logger.error(f"Squad API HTTP error: {error_detail}")
                return {"error": f"Squad API error: {error_detail}"}
                
            except Exception as e:
                logger.error(f"Unexpected error creating virtual account: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}
    
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
        
        url = f"{self.base_url}/virtual-account/business"
        
        payload = {
            "customer_identifier": customer_identifier,
            "business_name": business_name,
            "mobile_num": user.phone_number or "08000000000",
            "email": user.email,
        }
        
        # Add BVN if available
        if user.bvn:
            payload["bvn"] = user.bvn
        
        logger.info(f"Creating business virtual account for user {user.id}: {business_name}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("success"):
                    # Save virtual account to database
                    va_data = result.get("data", {})
                    virtual_account = VirtualAccount(
                        user_id=user.id,
                        customer_identifier=customer_identifier,
                        virtual_account_number=va_data.get("virtual_account_number"),
                        bank_code=va_data.get("bank_code", "058"),
                        account_type=VirtualAccountType.BUSINESS,
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
                
            except httpx.HTTPStatusError as e:
                error_detail = self._extract_error_message(e.response)
                logger.error(f"Squad API HTTP error: {error_detail}")
                return {"error": f"Squad API error: {error_detail}"}
                
            except Exception as e:
                logger.error(f"Unexpected error creating business virtual account: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}
    
    async def simulate_payment(
        self,
        virtual_account_number: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Simulate a payment to a virtual account (sandbox only).
        """
        if not self.secret_key:
            return {"error": "Virtual account service not configured"}
        
        url = f"{self.base_url}/virtual-account/simulate/payment"
        
        # Convert amount to kobo
        amount_in_kobo = int(amount * 100)
        
        payload = {
            "virtual_account_number": virtual_account_number,
            "amount": str(amount_in_kobo)
        }
        
        logger.info(f"Simulating payment: {amount} NGN to {virtual_account_number}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Payment simulation result: {result}")
                return result
                
            except httpx.HTTPStatusError as e:
                error_detail = self._extract_error_message(e.response)
                logger.error(f"Squad API HTTP error during payment simulation: {error_detail}")
                return {"error": f"Squad API error: {error_detail}"}
                
            except Exception as e:
                logger.error(f"Unexpected error during payment simulation: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}
    
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
    
    def process_webhook_transaction(
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
            
            # Find the virtual account
            virtual_account = crud_virtual_account.get_virtual_account_by_number(
                db, virtual_account_number=virtual_account_number
            )
            
            if not virtual_account:
                logger.error(f"Virtual account not found: {virtual_account_number}")
                return {"error": "Virtual account not found"}
            
            # Calculate platform commission split
            total_platform_commission = settled_amount * virtual_account.platform_commission_rate
            insureflow_commission = settled_amount * virtual_account.insureflow_commission_rate
            habari_commission = settled_amount * virtual_account.habari_commission_rate
            
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
            if virtual_account.auto_settlement and virtual_account.current_balance >= virtual_account.settlement_threshold:
                self._initiate_auto_settlement(db, virtual_account)
            
            logger.info(f"Webhook transaction processed successfully: {transaction_ref}")
            logger.info(f"Commission split - InsureFlow: ₦{insureflow_commission}, Habari: ₦{habari_commission}")
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
        This would typically involve transferring funds to the user's main account.
        """
        try:
            # Calculate net amount after platform commission
            net_amount = virtual_account.net_amount_after_commission
            
            logger.info(f"Auto-settlement initiated for VA {virtual_account.virtual_account_number}: ₦{net_amount}")
            logger.info(f"Platform commission: ₦{virtual_account.total_platform_commission} (InsureFlow: ₦{virtual_account.insureflow_commission_amount}, Habari: ₦{virtual_account.habari_commission_amount})")
            
            # Create settlement transaction record
            settlement_transaction = VirtualAccountTransaction(
                virtual_account_id=virtual_account.id,
                transaction_reference=f"SETTLE_{virtual_account.id}_{int(datetime.now().timestamp())}",
                transaction_type=TransactionType.SETTLEMENT,
                transaction_indicator=TransactionIndicator.D,
                status=TransactionStatus.PENDING,
                principal_amount=net_amount,
                settled_amount=net_amount,
                transaction_date=datetime.utcnow(),
                remarks=f"Auto-settlement for virtual account {virtual_account.virtual_account_number}"
            )
            
            db.add(settlement_transaction)
            
            # Update virtual account balance
            virtual_account.current_balance -= net_amount
            
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