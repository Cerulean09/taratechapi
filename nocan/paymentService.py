import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

logger = logging.getLogger(__name__)

class HarsyaPaymentService:
    """Service class to handle Harsya payment gateway integration"""
    
    def __init__(self):
        # Harsya API configuration - you'll need to replace these with your actual credentials
        self.baseUrl = "https://api.harsya.com"  # Replace with actual Harsya API URL
        self.clientId = "your_client_id"  # Replace with your actual client ID
        self.clientSecret = "your_client_secret"  # Replace with your actual client secret
        self.accessToken = None
        self.tokenExpiry = None
    
    def getToken(self) -> Optional[str]:
        """Get access token from Harsya API"""
        try:
            url = f"{self.baseUrl}/auth/token"
            payload = {
                "clientId": self.clientId,
                "clientSecret": self.clientSecret,
                "grantType": "client_credentials"
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == '00':
                self.accessToken = data['data']['accessToken']
                # Token expires in 15 minutes (900 seconds)
                self.tokenExpiry = datetime.now() + timedelta(seconds=900)
                return self.accessToken
            else:
                logger.error(f"Failed to get token: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting token: {str(e)}")
            return None
    
    def _ensureValidToken(self) -> bool:
        """Ensure we have a valid access token"""
        if (self.accessToken is None or 
            self.tokenExpiry is None or 
            datetime.now() >= self.tokenExpiry):
            return self.getToken() is not None
        return True
    
    def getPaymentMethodConfig(self, accessToken: str) -> Optional[str]:
        """Get payment method configuration"""
        try:
            url = f"{self.baseUrl}/payment-methods/config"
            headers = {"Authorization": f"Bearer {accessToken}"}
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error getting payment method config: {str(e)}")
            return None
    
    def createPayment(self, 
                     accessToken: str,
                     invoiceNo: str,
                     amount: float,
                     paymentMethodObject: Dict[str, Any],
                     paymentMethodOptions: Dict[str, Any],
                     clientReferenceId: str,
                     mode: str = "REDIRECT",
                     redirectUrl: Optional[str] = None,
                     autoConfirm: bool = True,
                     statementDescriptor: str = "Harsya",
                     expiryAt: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a new payment"""
        try:
            if not self._ensureValidToken():
                return None
            
            url = f"{self.baseUrl}/payments"
            headers = {
                "Authorization": f"Bearer {accessToken}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "invoiceNo": invoiceNo,
                "amount": {
                    "value": amount,
                    "currency": "IDR"
                },
                "paymentMethod": paymentMethodObject,
                "paymentMethodOptions": paymentMethodOptions,
                "clientReferenceId": clientReferenceId,
                "mode": mode,
                "autoConfirm": autoConfirm,
                "statementDescriptor": statementDescriptor
            }
            
            if redirectUrl:
                payload["redirectUrl"] = redirectUrl
            
            if expiryAt:
                payload["expiryAt"] = expiryAt
            
            if metadata:
                payload["metadata"] = metadata
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return None
    
    def getPaymentDetails(self, paymentId: str, accessToken: str) -> Optional[str]:
        """Get payment details by payment ID"""
        try:
            url = f"{self.baseUrl}/payments/{paymentId}"
            headers = {"Authorization": f"Bearer {accessToken}"}
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error getting payment details: {str(e)}")
            return None
    
    def confirmPayment(self, 
                      paymentId: str,
                      accessToken: str,
                      paymentMethodObject: Dict[str, Any],
                      paymentMethodOptions: Dict[str, Any],
                      simulateSuccessPayment: bool = False) -> bool:
        """Confirm payment (can be used for simulation in testing)"""
        try:
            if not self._ensureValidToken():
                return False
            
            url = f"{self.baseUrl}/payments/{paymentId}/confirm"
            headers = {
                "Authorization": f"Bearer {accessToken}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "paymentMethod": paymentMethodObject,
                "paymentMethodOptions": paymentMethodOptions
            }
            
            if simulateSuccessPayment:
                payload["simulateSuccess"] = True
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('code') == '00' and data.get('data', {}).get('status') == 'SUCCESS'
            
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return False

# Global instance
harsyaPaymentService = HarsyaPaymentService() 