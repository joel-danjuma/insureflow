"""
Service for interacting with the Squad Co API.
"""
import hashlib
import hmac
import httpx
from app.core.config import settings

class SquadCoService:
    def __init__(self):
        self.base_url = settings.SQUAD_BASE_URL
        self.secret_key = settings.SQUAD_SECRET_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def verify_webhook_signature(self, request_body: bytes, signature: str) -> bool:
        """
        Verifies the signature of a webhook request from Squad Co.
        """
        if not signature:
            return False
            
        hmac_hash = hmac.new(
            self.secret_key.encode('utf-8'),
            request_body,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(hmac_hash, signature)

    async def initiate_payment(self, amount: int, email: str, currency: str, metadata: dict = None):
        """
        Initiates a payment transaction with Squad Co.
        """
        url = f"{self.base_url}/transaction/initiate"
        payload = {
            "amount": amount * 100,  # Convert to kobo
            "email": email,
            "currency": currency,
            "metadata": metadata or {},
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Handle specific HTTP errors
                return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
            except httpx.RequestError as e:
                # Handle network-related errors
                return {"error": f"An error occurred while requesting from Squad Co: {e}"}

# Create a single instance of the service to be used across the application
squad_co_service = SquadCoService() 