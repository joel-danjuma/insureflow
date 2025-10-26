"""
Service for interacting with the Squad Co API.
"""
import hashlib
import hmac
import httpx
import logging
from app.core.config import settings
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SquadCoService:
    def __init__(self):
        self.base_url = settings.SQUAD_BASE_URL
        self.secret_key = settings.SQUAD_SECRET_KEY
        
        # Validate configuration
        if not self.secret_key or self.secret_key == "":
            logger.warning("Squad secret key not configured. Payment functionality will not work.")
        
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

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

    async def create_virtual_account(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a virtual account with Squad Co.
        """
        if not self.secret_key:
            logger.error("Squad secret key not configured - cannot create virtual account")
            return {"error": "Virtual account service not configured"}

        url = f"{self.base_url}/virtual-account"
        logger.info("📞 Calling Squad Co API for Virtual Account Creation")
        logger.info(f"📋 Virtual Account Request Payload: {payload}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                logger.info(f"Squad API Response: {result}")
                return result
            except httpx.HTTPStatusError as e:
                error_detail = self._extract_error_message(e.response)
                logger.error(f"Squad API HTTP error: {error_detail}")
                return {"error": f"Squad API error: {error_detail}"}
            except Exception as e:
                logger.error(f"Unexpected error creating virtual account: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}

    async def simulate_payment(self, virtual_account_number: str, amount: Decimal) -> Dict[str, Any]:
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
        logger.info(f"Simulate Payment Payload: {payload}")
        
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

    def verify_webhook_signature(self, request_body: bytes, signature: str) -> bool:
        """
        Verifies the signature of a webhook request from Squad Co.
        """
        if not signature:
            logger.warning("No signature provided for webhook verification")
            return False
            
        if not self.secret_key or self.secret_key == "":
            logger.error("Squad secret key not configured - cannot verify webhook signature")
            return False
            
        hmac_hash = hmac.new(
            self.secret_key.encode('utf-8'),
            request_body,
            hashlib.sha512
        ).hexdigest()
        
        is_valid = hmac.compare_digest(hmac_hash, signature)
        if not is_valid:
            logger.warning("Invalid webhook signature received")
        
        return is_valid

    async def initiate_payment(self, amount: int, email: str, currency: str, metadata: dict = None):
        """
        Initiates a payment transaction with Squad Co.
        Amount should be in base currency (Naira), not kobo - will be converted here.
        """
        if not self.secret_key or self.secret_key == "":
            logger.error("Squad secret key not configured - cannot initiate payment")
            return {"error": "Payment gateway not configured. Please contact support."}
        
        url = f"{self.base_url}/transaction/initiate"
        
        # Convert amount to kobo (Squad requires lowest currency unit)
        amount_in_kobo = int(amount * 100)
        
        payload = {
            "amount": amount_in_kobo,
            "email": email,
            "currency": currency,
            "initiate_type": "inline",  # Required field according to Squad docs
            "transaction_ref": f"INSURE_{int(datetime.now().timestamp())}_{amount_in_kobo}",  # Generate unique ref
            "callback_url": f"{settings.SQUAD_WEBHOOK_URL or 'http://localhost:8000/api/v1/payments/webhook'}",
            "metadata": metadata or {},
        }
        
        logger.info(f"Initiating Squad payment: amount={amount_in_kobo} kobo, email={email}, ref={payload['transaction_ref']}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:  # Increased timeout
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                
                # Log the response for debugging
                logger.info(f"Squad API response status: {response.status_code}")
                logger.info(f"Squad API response body: {response.text}")
                
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Squad payment initiated successfully: {result.get('data', {}).get('transaction_ref', 'N/A')}")
                return result
                
            except httpx.HTTPStatusError as e:
                # Handle specific HTTP errors
                error_detail = f"HTTP {e.response.status_code}"
                try:
                    error_data = e.response.json()
                    if 'message' in error_data:
                        error_detail = error_data['message']
                    elif 'errors' in error_data:
                        error_detail = str(error_data['errors'])
                    elif 'data' in error_data and 'message' in error_data['data']:
                        error_detail = error_data['data']['message']
                except:
                    error_detail = e.response.text
                
                logger.error(f"Squad API HTTP error: {error_detail}")
                return {"error": f"Squad API error: {error_detail}"}
                
            except httpx.RequestError as e:
                # Handle network-related errors
                logger.error(f"Network error contacting Squad: {str(e)}")
                return {"error": f"Network error while contacting Squad: {str(e)}"}
                
            except Exception as e:
                logger.error(f"Unexpected error in Squad payment initiation: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}

    async def verify_payment(self, transaction_ref: str):
        """
        Verify a payment transaction with Squad Co.
        """
        if not self.secret_key or self.secret_key == "":
            logger.error("Squad secret key not configured - cannot verify payment")
            return {"error": "Payment gateway not configured. Please contact support."}
        
        url = f"{self.base_url}/transaction/verify/{transaction_ref}"
        
        logger.info(f"Verifying Squad payment: {transaction_ref}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers)
                
                logger.info(f"Squad verify response status: {response.status_code}")
                logger.info(f"Squad verify response body: {response.text}")
                
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Squad payment verification result: {result.get('data', {}).get('transaction_status', 'Unknown')}")
                return result
                
            except httpx.HTTPStatusError as e:
                error_detail = f"HTTP {e.response.status_code}"
                try:
                    error_data = e.response.json()
                    if 'message' in error_data:
                        error_detail = error_data['message']
                except:
                    error_detail = e.response.text
                
                logger.error(f"Squad API verification error: {error_detail}")
                return {"error": f"Squad API verification error: {error_detail}"}
                
            except Exception as e:
                logger.error(f"Unexpected error in Squad payment verification: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}

# Create a single instance of the service to be used across the application
squad_co_service = SquadCoService() 