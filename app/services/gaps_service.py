"""
GAPS Service for InsureFlow application.
Handles integration with GTBank's GAPS for bulk and single transfers.
"""
import httpx
import logging
from typing import Dict, Any, Optional, List
from xml.etree import ElementTree as ET

from app.core.config import settings

logger = logging.getLogger(__name__)


class GapsService:
    """Service for managing GAPS transfers."""

    def __init__(self):
        self.base_url = settings.GAPS_BASE_URL
        self.access_code = settings.GAPS_ACCESS_CODE
        self.username = settings.GAPS_USERNAME
        self.password = settings.GAPS_PASSWORD
        self.channel = settings.GAPS_CHANNEL

        if not all([self.base_url, self.access_code, self.username, self.password, self.channel]):
            logger.warning("GAPS service not fully configured. Settlement functionality will not work.")

        self.headers = {
            "Content-Type": "application/xml",
        }

    async def _send_request(self, endpoint: str, payload: str) -> Dict[str, Any]:
        """Send a request to the GAPS API."""
        if not all([self.base_url, self.access_code, self.username, self.password, self.channel]):
            return {"error": "GAPS service not configured"}

        url = f"{self.base_url}/{endpoint}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, content=payload, headers=self.headers)
                response.raise_for_status()
                return self._parse_response(response.text)
            except httpx.HTTPStatusError as e:
                logger.error(f"GAPS API HTTP error: {e.response.text}")
                return {"error": f"GAPS API error: {e.response.text}"}
            except Exception as e:
                logger.error(f"Unexpected error communicating with GAPS: {str(e)}")
                return {"error": f"Unexpected error: {str(e)}"}

    def _parse_response(self, xml_string: str) -> Dict[str, Any]:
        """Parse the XML response from GAPS."""
        try:
            root = ET.fromstring(xml_string)
            response_element = root.find(".//Response")
            if response_element is not None:
                response_xml = ET.fromstring(response_element.text)
                code = response_xml.find("CODE").text
                description = response_xml.find("DESC").text
                return {"code": code, "description": description}
            return {"error": "Invalid response format from GAPS"}
        except Exception as e:
            logger.error(f"Error parsing GAPS response: {str(e)}")
            return {"error": "Error parsing GAPS response"}

    async def initiate_single_transfer(self, transfer_details: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate a single transfer."""
        # NOTE: GAPS requires RSA encryption for sensitive fields.
        # This is a simplified example and does not include encryption.
        xml_request = f"""
        <SingleTransferRequest>
            <transdetails>
                <transaction>
                    <amount>{transfer_details['amount']}</amount>
                    <paymentdate>{transfer_details['payment_date']}</paymentdate>
                    <reference>{transfer_details['reference']}</reference>
                    <remarks>{transfer_details['remarks']}</remarks>
                    <vendorcode>{transfer_details['vendor_code']}</vendorcode>
                    <vendorname>{transfer_details['vendor_name']}</vendorname>
                    <vendoracctnumber>{transfer_details['vendor_acct_number']}</vendoracctnumber>
                    <vendorbankcode>{transfer_details['vendor_bank_code']}</vendorbankcode>
                    <customeracctnumber>{transfer_details['customer_acct_number']}</customeracctnumber>
                </transaction>
            </transdetails>
            <accesscode>{self.access_code}</accesscode>
            <username>{self.username}</username>
            <password>{self.password}</password>
            <channel>{self.channel}</channel>
        </SingleTransferRequest>
        """
        return await self._send_request("SingleTransfers_Enc", xml_request)

    async def initiate_bulk_transfer(self, transfers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Initiate a bulk transfer."""
        transactions_xml = ""
        for transfer in transfers:
            transactions_xml += f"""
            <transaction>
                <amount>{transfer['amount']}</amount>
                <paymentdate>{transfer['payment_date']}</paymentdate>
                <reference>{transfer['reference']}</reference>
                <remarks>{transfer['remarks']}</remarks>
                <vendorcode>{transfer['vendor_code']}</vendorcode>
                <vendorname>{transfer['vendor_name']}</vendorname>
                <vendoracctnumber>{transfer['vendor_acct_number']}</vendoracctnumber>
                <vendorbankcode>{transfer['vendor_bank_code']}</vendorbankcode>
                <customeracctnumber>{transfer['customer_acct_number']}</customeracctnumber>
            </transaction>
            """

        xml_request = f"""
        <BulkTransfers_Enc>
            <transdetails>
                <transactions>
                    {transactions_xml}
                </transactions>
            </transdetails>
            <accesscode>{self.access_code}</accesscode>
            <username>{self.username}</username>
            <password>{self.password}</password>
            <channel>{self.channel}</channel>
        </BulkTransfers_Enc>
        """
        return await self._send_request("BulkTransfers_Enc", xml_request)


gaps_service = GapsService()
