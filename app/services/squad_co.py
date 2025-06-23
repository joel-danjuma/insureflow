"""
Service for interacting with the Squad Co API.
"""
import hashlib
import hmac
import httpx
import logging
from app.core.config import settings

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
            "metadata": metadata or {},
        }
        
        logger.info(f"Initiating Squad payment: amount={amount_in_kobo} kobo, email={email}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
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

# Create a single instance of the service to be used across the application
squad_co_service = SquadCoService() 