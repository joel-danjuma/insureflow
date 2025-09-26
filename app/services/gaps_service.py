"""
GAPS Integration Service for InsureFlow application.
Handles GTBank GAPS bulk transfers and settlements.
"""
import httpx
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import os

from app.core.config import settings

logger = logging.getLogger(__name__)

class GAPSService:
    """Service for managing GAPS bulk transfers and settlements."""
    
    def __init__(self):
        self.base_url = getattr(settings, 'GAPS_BASE_URL', "https://gtweb6.gtbank.com/GSTPS/GAPS_FileUploader/FileUploader.asmx")
        self.customer_id = getattr(settings, 'GAPS_CUSTOMER_ID', "")
        self.username = getattr(settings, 'GAPS_USERNAME', "")
        self.password = getattr(settings, 'GAPS_PASSWORD', "")
        self.channel = getattr(settings, 'GAPS_CHANNEL', "GSTP")
        self.public_key = self._load_public_key()
        
        if not all([self.customer_id, self.username, self.password]):
            logger.warning("GAPS credentials not configured. Settlement functionality will not work.")
    
    def _load_public_key(self):
        """Load GAPS public key for encryption."""
        try:
            # Test public key from GAPS documentation
            public_key_pem = getattr(settings, 'GAPS_PUBLIC_KEY', "") or """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCrtPgIUBsQscypy+2A2l6oHKlL
RTgD4hlrYKW9IrAK4ll0FPndJ3i57CioPalYKdNMF9+K4mFaGfT3dAMRSgWWWDea
erHx35VLgdX/wFTN5Zf1QYGeWiKyAmCAXoPwtlfvlLqsr9NMBJ3Ua+fFqSC4/6Th
hudMlrxNL/ut/kd+pQIDAQAB
-----END PUBLIC KEY-----"""
            
            return serialization.load_pem_public_key(public_key_pem.encode())
        except Exception as e:
            logger.error(f"Failed to load GAPS public key: {e}")
            return None
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt data using GAPS public key."""
        if not self.public_key:
            raise Exception("GAPS public key not loaded")
        
        try:
            encrypted = self.public_key.encrypt(
                data.encode(),
                padding.PKCS1v15()
            )
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    async def process_bulk_settlement(
        self,
        settlements: List[Dict[str, Any]],
        settlement_account: str
    ) -> Dict[str, Any]:
        """
        Process bulk settlement to insurance firms using GAPS.
        
        Args:
            settlements: List of settlement records
            settlement_account: InsureFlow settlement account (source)
        """
        if not self.public_key:
            return {"error": "GAPS service not properly configured"}
        
        try:
            # Build XML for bulk transfer
            transactions_xml = self._build_bulk_transactions_xml(settlements, settlement_account)
            
            # Encrypt sensitive data
            encrypted_customer_id = self._encrypt_data(self.customer_id)
            encrypted_username = self._encrypt_data(self.username)
            encrypted_password = self._encrypt_data(self.password)
            
            # Build request payload
            request_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <BulkTransfers_Enc xmlns="http://tempuri.org/">
      <xmlRequest>
        <transdetails>{transactions_xml}</transdetails>
        <accesscode>{encrypted_customer_id}</accesscode>
        <username>{encrypted_username}</username>
        <password>{encrypted_password}</password>
        <channel>{self.channel}</channel>
      </xmlRequest>
    </BulkTransfers_Enc>
  </soap:Body>
</soap:Envelope>"""
            
            # Call GAPS BulkTransfers_Enc endpoint
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    content=request_xml,
                    headers={
                        "Content-Type": "text/xml; charset=utf-8",
                        "SOAPAction": "http://tempuri.org/BulkTransfers_Enc"
                    }
                )
                response.raise_for_status()
                
                # Parse XML response
                response_data = self._parse_gaps_response(response.text)
                
                logger.info(f"GAPS bulk settlement response: {response_data}")
                return response_data
                
        except Exception as e:
            logger.error(f"GAPS bulk settlement failed: {str(e)}")
            return {"error": f"Settlement failed: {str(e)}"}
    
    def _build_bulk_transactions_xml(
        self,
        settlements: List[Dict[str, Any]],
        settlement_account: str
    ) -> str:
        """Build XML string for bulk transactions."""
        transactions = []
        
        for settlement in settlements:
            try:
                # Encrypt sensitive data
                amount_kobo = str(int(settlement['amount'] * 100))  # Convert to kobo
                encrypted_amount = self._encrypt_data(amount_kobo)
                encrypted_vendor_account = self._encrypt_data(settlement['beneficiary_account'])
                encrypted_customer_account = self._encrypt_data(settlement_account)
                
                transaction_xml = f"""<transaction>
<amount>{encrypted_amount}</amount>
<paymentdate>{settlement['payment_date']}</paymentdate>
<reference>{settlement['reference']}</reference>
<remarks>{settlement['remarks']}</remarks>
<vendorcode>{settlement['vendor_code']}</vendorcode>
<vendorname>{settlement['beneficiary_name']}</vendorname>
<vendoracctnumber>{encrypted_vendor_account}</vendoracctnumber>
<vendorbankcode>{settlement['bank_code']}</vendorbankcode>
<customeracctnumber>{encrypted_customer_account}</customeracctnumber>
</transaction>"""
                transactions.append(transaction_xml)
            except Exception as e:
                logger.error(f"Failed to build transaction XML for settlement {settlement.get('reference')}: {e}")
                continue
        
        return f"<transactions>{''.join(transactions)}</transactions>"
    
    def _parse_gaps_response(self, response_text: str) -> Dict[str, Any]:
        """Parse GAPS XML response."""
        try:
            # Parse the SOAP response
            root = ET.fromstring(response_text)
            
            # Find the response element
            response_element = root.find('.//{http://tempuri.org/}BulkTransfers_EncResponse/{http://tempuri.org/}BulkTransfers_EncResult')
            
            if response_element is not None:
                response_content = response_element.text
                
                # Parse the inner XML response
                if response_content:
                    inner_root = ET.fromstring(response_content)
                    code = inner_root.find('.//code')
                    message = inner_root.find('.//message')
                    
                    code_value = code.text if code is not None else "Unknown"
                    message_value = message.text if message is not None else "No message"
                    
                    # Check if successful (code 1000)
                    success = code_value == "1000"
                    
                    return {
                        "success": success,
                        "code": code_value,
                        "message": message_value,
                        "raw_response": response_text
                    }
                else:
                    return {"error": "Empty response content", "raw_response": response_text}
            else:
                return {"error": "Invalid response format", "raw_response": response_text}
                
        except Exception as e:
            logger.error(f"Failed to parse GAPS response: {e}")
            return {"error": f"Response parsing failed: {str(e)}", "raw_response": response_text}
    
    async def query_transaction_status(self, transaction_ref: str) -> Dict[str, Any]:
        """Query the status of a GAPS transaction."""
        if not self.public_key:
            return {"error": "GAPS service not properly configured"}
        
        try:
            # Encrypt credentials
            encrypted_customer_id = self._encrypt_data(self.customer_id)
            encrypted_username = self._encrypt_data(self.username)
            encrypted_password = self._encrypt_data(self.password)
            
            # Build SOAP request
            request_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TransactionRequery_Enc xmlns="http://tempuri.org/">
      <transref>{transaction_ref}</transref>
      <customerid>{encrypted_customer_id}</customerid>
      <username>{encrypted_username}</username>
      <password>{encrypted_password}</password>
      <channel>{self.channel}</channel>
    </TransactionRequery_Enc>
  </soap:Body>
</soap:Envelope>"""
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    content=request_xml,
                    headers={
                        "Content-Type": "text/xml; charset=utf-8",
                        "SOAPAction": "http://tempuri.org/TransactionRequery_Enc"
                    }
                )
                response.raise_for_status()
                
                return self._parse_gaps_response(response.text)
                
        except Exception as e:
            logger.error(f"GAPS transaction query failed: {str(e)}")
            return {"error": f"Query failed: {str(e)}"}

# Global service instance
gaps_service = GAPSService()
