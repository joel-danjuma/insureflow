"""
GAPS (GTBank Automated Payment System) Integration Service

This service handles:
1. RSA encryption for sensitive data
2. XML formatting for GAPS API requests
3. Bulk transfer processing
4. Transaction status queries
5. Account validation

Based on GAPS Integration Requirements v1.0.3
"""

import base64
import xml.etree.ElementTree as ET
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
import requests
import logging
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

from app.core.config import settings

logger = logging.getLogger(__name__)


class GAPSEncryption:
    """Handle RSA encryption for GAPS API"""
    
    def __init__(self, public_key_pem: str):
        """Initialize with GAPS public key"""
        self.public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
    
    def encrypt(self, data: str) -> str:
        """Encrypt data using RSA public key"""
        try:
            encrypted = self.public_key.encrypt(
                data.encode('utf-8'),
                padding.PKCS1v15()
            )
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise


class GAPSTransactionBuilder:
    """Build XML transactions for GAPS API"""
    
    def __init__(self, encryption: GAPSEncryption):
        self.encryption = encryption
    
    def build_single_transfer(
        self,
        amount: Decimal,
        vendor_account: str,
        vendor_bank_code: str,
        vendor_name: str,
        vendor_code: str,
        customer_account: str,
        reference: str,
        remarks: str,
        payment_date: date = None
    ) -> str:
        """Build single transfer XML"""
        
        if payment_date is None:
            payment_date = date.today()
        
        # Encrypt sensitive fields
        encrypted_amount = self.encryption.encrypt(str(amount))
        encrypted_vendor_account = self.encryption.encrypt(vendor_account)
        encrypted_customer_account = self.encryption.encrypt(customer_account)
        
        # Build XML
        transaction = ET.Element("transaction")
        
        ET.SubElement(transaction, "amount").text = encrypted_amount
        ET.SubElement(transaction, "paymentdate").text = payment_date.strftime("%Y-%m-%d")
        ET.SubElement(transaction, "reference").text = reference
        ET.SubElement(transaction, "remarks").text = remarks
        ET.SubElement(transaction, "vendorcode").text = vendor_code
        ET.SubElement(transaction, "vendorname").text = vendor_name
        ET.SubElement(transaction, "vendoracctnumber").text = encrypted_vendor_account
        ET.SubElement(transaction, "vendorbankcode").text = vendor_bank_code
        ET.SubElement(transaction, "customeracctnumber").text = encrypted_customer_account
        
        return ET.tostring(transaction, encoding='unicode')
    
    def build_bulk_transfers(self, transfers: List[Dict[str, Any]]) -> str:
        """Build bulk transfers XML"""
        
        transactions = ET.Element("transactions")
        
        for transfer in transfers:
            transaction_xml = self.build_single_transfer(
                amount=transfer['amount'],
                vendor_account=transfer['vendor_account'],
                vendor_bank_code=transfer['vendor_bank_code'],
                vendor_name=transfer['vendor_name'],
                vendor_code=transfer['vendor_code'],
                customer_account=transfer['customer_account'],
                reference=transfer['reference'],
                remarks=transfer['remarks'],
                payment_date=transfer.get('payment_date')
            )
            
            # Parse and append to transactions
            transaction_element = ET.fromstring(transaction_xml)
            transactions.append(transaction_element)
        
        return ET.tostring(transactions, encoding='unicode')


class GAPSAPIClient:
    """GAPS API Client for making requests"""
    
    def __init__(self):
        self.base_url = settings.GAPS_BASE_URL
        self.encryption = GAPSEncryption(settings.GAPS_PUBLIC_KEY)
        self.transaction_builder = GAPSTransactionBuilder(self.encryption)
        
        # Encrypt credentials
        self.encrypted_username = self.encryption.encrypt(settings.GAPS_USERNAME)
        self.encrypted_password = self.encryption.encrypt(settings.GAPS_PASSWORD)
        self.encrypted_customer_id = self.encryption.encrypt(settings.GAPS_CUSTOMER_ID)
        self.channel = settings.GAPS_CHANNEL
    
    def _build_request_xml(self, trans_details: str, method: str) -> str:
        """Build complete request XML"""
        
        # Escape XML for transdetails
        escaped_trans_details = trans_details.replace('<', '&lt;').replace('>', '&gt;')
        
        if method == "BulkTransfers_Enc":
            root = ET.Element("BulkTransfers_Enc")
        elif method == "SingleTransfers_Enc":
            root = ET.Element("SingleTransferRequest")
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        ET.SubElement(root, "transdetails").text = escaped_trans_details
        ET.SubElement(root, "accesscode").text = self.encrypted_customer_id
        ET.SubElement(root, "username").text = self.encrypted_username
        ET.SubElement(root, "password").text = self.encrypted_password
        ET.SubElement(root, "channel").text = self.channel
        
        return ET.tostring(root, encoding='unicode')
    
    def bulk_transfer(self, transfers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute bulk transfer via GAPS"""
        
        try:
            # Build transaction XML
            trans_details = self.transaction_builder.build_bulk_transfers(transfers)
            
            # Build complete request
            request_xml = self._build_request_xml(trans_details, "BulkTransfers_Enc")
            
            # Make API call
            response = requests.post(
                f"{self.base_url}",
                data={"xmlRequest": request_xml},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse response
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"Bulk transfer failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_code": "1008",
                "response_description": "System error"
            }
    
    def single_transfer(self, transfer: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single transfer via GAPS"""
        
        try:
            # Build transaction XML
            trans_details = self.transaction_builder.build_single_transfer(**transfer)
            
            # Build complete request
            request_xml = self._build_request_xml(trans_details, "SingleTransfers_Enc")
            
            # Make API call
            response = requests.post(
                f"{self.base_url}",
                data={"xmlRequest": request_xml},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse response
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"Single transfer failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_code": "1008",
                "response_description": "System error"
            }
    
    def query_transaction(self, transaction_reference: str) -> Dict[str, Any]:
        """Query transaction status"""
        
        try:
            # Build requery request
            root = ET.Element("TransactionRequeryRequest")
            ET.SubElement(root, "transref").text = transaction_reference
            ET.SubElement(root, "customerid").text = self.encrypted_customer_id
            ET.SubElement(root, "username").text = self.encrypted_username
            ET.SubElement(root, "password").text = self.encrypted_password
            ET.SubElement(root, "channel").text = self.channel
            
            request_xml = ET.tostring(root, encoding='unicode')
            
            # Make API call
            response = requests.post(
                f"{self.base_url}",
                data={"xmlRequest": request_xml},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse response
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"Transaction query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_code": "1008",
                "response_description": "System error"
            }
    
    def validate_account(self, account_number: str, bank_code: str = None) -> Dict[str, Any]:
        """Validate account number"""
        
        try:
            # Encrypt account number
            encrypted_account = self.encryption.encrypt(account_number)
            
            if bank_code:
                # Other bank validation
                root = ET.Element("GetAccountInOtherBank_Enc")
                ET.SubElement(root, "accountNo").text = encrypted_account
                ET.SubElement(root, "bankcode").text = bank_code
            else:
                # GTB validation
                root = ET.Element("GetAccountInGTB_Enc")
                ET.SubElement(root, "accountNo").text = encrypted_account
            
            ET.SubElement(root, "customerid").text = self.encrypted_customer_id
            ET.SubElement(root, "username").text = self.encrypted_username
            ET.SubElement(root, "password").text = self.encrypted_password
            ET.SubElement(root, "channel").text = self.channel
            
            request_xml = ET.tostring(root, encoding='unicode')
            
            # Make API call
            response = requests.post(
                f"{self.base_url}",
                data={"xmlRequest": request_xml},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse response
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"Account validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_code": "1008",
                "response_description": "System error"
            }
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse GAPS API response"""
        
        try:
            # Parse XML response
            root = ET.fromstring(response_text)
            
            # Extract response data
            response_element = root.find(".//Response")
            if response_element is not None:
                response_content = response_element.text
                
                # Parse response content (usually contains code and description)
                if "1000" in response_content:
                    return {
                        "success": True,
                        "response_code": "1000",
                        "response_description": "Transaction Successful",
                        "raw_response": response_content
                    }
                else:
                    # Extract error code and description
                    return {
                        "success": False,
                        "response_code": "1001",  # Default to auth error
                        "response_description": "Transaction Failed",
                        "raw_response": response_content
                    }
            
            return {
                "success": False,
                "response_code": "1008",
                "response_description": "Invalid response format",
                "raw_response": response_text
            }
            
        except Exception as e:
            logger.error(f"Response parsing failed: {e}")
            return {
                "success": False,
                "response_code": "1008",
                "response_description": f"Response parsing error: {str(e)}",
                "raw_response": response_text
            }


# Response code mappings
GAPS_RESPONSE_CODES = {
    "1000": {"status": "SUCCESS", "description": "Transaction Successful"},
    "1001": {"status": "FAILED", "description": "Invalid Username/Password"},
    "1002": {"status": "FAILED", "description": "Access disabled or not activated"},
    "1003": {"status": "FAILED", "description": "Access to system is locked"},
    "1004": {"status": "FAILED", "description": "Password expired"},
    "1005": {"status": "FAILED", "description": "Invalid encrypted value"},
    "1006": {"status": "FAILED", "description": "Invalid xml format in transaction details"},
    "1007": {"status": "PENDING", "description": "Transaction validation error"},
    "1008": {"status": "PENDING", "description": "System error"},
    "1010": {"status": "FAILED", "description": "Failed. Only single transaction allowed"},
    "1100": {"status": "PENDING", "description": "Transaction is being processed"},
}


def get_gaps_client() -> GAPSAPIClient:
    """Get configured GAPS API client"""
    return GAPSAPIClient()
