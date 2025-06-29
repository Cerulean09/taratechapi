"""
URL Configuration Utility for TaraTech API
This module provides centralized access to all API endpoints.
"""

from django.conf import settings
from typing import Dict, Any

class URLConfig:
    """Centralized URL configuration utility"""
    
    @staticmethod
    def get_base_url() -> str:
        """Get the base URL for the application"""
        return settings.BASE_URL
    
    @staticmethod
    def get_api_base_url() -> str:
        """Get the API base URL"""
        return settings.API_BASE_URL
    
    @staticmethod
    def get_payment_api_base_url() -> str:
        """Get the payment API base URL"""
        return settings.PAYMENT_API_BASE_URL
    
    @staticmethod
    def get_endpoint(endpoint_name: str, **kwargs) -> str:
        """
        Get a specific API endpoint URL
        
        Args:
            endpoint_name: Name of the endpoint from settings.API_ENDPOINTS
            **kwargs: Parameters to format into the URL (e.g., payment_id)
        
        Returns:
            Formatted URL string
        """
        if endpoint_name not in settings.API_ENDPOINTS:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")
        
        url_template = settings.API_ENDPOINTS[endpoint_name]
        return url_template.format(**kwargs)
    
    @staticmethod
    def get_all_endpoints() -> Dict[str, str]:
        """Get all API endpoints"""
        return settings.API_ENDPOINTS.copy()
    
    @staticmethod
    def get_payment_endpoints() -> Dict[str, str]:
        """Get payment-specific endpoints"""
        return {
            'create': settings.API_ENDPOINTS['payment_create'],
            'status_template': settings.API_ENDPOINTS['payment_status'],
            'simulate_template': settings.API_ENDPOINTS['payment_simulate'],
        }
    
    @staticmethod
    def get_payment_status_url(payment_id: str) -> str:
        """Get payment status URL for a specific payment ID"""
        return settings.API_ENDPOINTS['payment_status'].format(payment_id=payment_id)
    
    @staticmethod
    def get_payment_simulate_url(payment_id: str) -> str:
        """Get payment simulate URL for a specific payment ID"""
        return settings.API_ENDPOINTS['payment_simulate'].format(payment_id=payment_id)
    
    @staticmethod
    def get_environment() -> str:
        """Get current environment"""
        return settings.ENVIRONMENT
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production"""
        return settings.ENVIRONMENT == 'production'
    
    @staticmethod
    def is_development() -> bool:
        """Check if running in development"""
        return settings.ENVIRONMENT == 'development'

# Convenience functions for easy access
def get_api_url(endpoint_name: str, **kwargs) -> str:
    """Get API URL for a specific endpoint"""
    return URLConfig.get_endpoint(endpoint_name, **kwargs)

def get_payment_create_url() -> str:
    """Get payment creation URL"""
    return URLConfig.get_endpoint('payment_create')

def get_payment_status_url(payment_id: str) -> str:
    """Get payment status URL"""
    return URLConfig.get_payment_status_url(payment_id)

def get_payment_simulate_url(payment_id: str) -> str:
    """Get payment simulate URL"""
    return URLConfig.get_payment_simulate_url(payment_id)

def get_base_url() -> str:
    """Get base URL"""
    return URLConfig.get_base_url()

def get_api_base_url() -> str:
    """Get API base URL"""
    return URLConfig.get_api_base_url() 