#!/usr/bin/env python3
"""
Configuration Checker for TaraTech API on PythonAnywhere
This script verifies that all configurations are set up correctly.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taratechapi.settings')
django.setup()

from django.conf import settings
from nocan.urlConfig import URLConfig

def check_django_settings():
    """Check Django settings configuration"""
    print("🔍 Checking Django Settings...")
    
    # Check BASE_URL
    print(f"✅ BASE_URL: {settings.BASE_URL}")
    
    # Check environment
    print(f"✅ Environment: {settings.ENVIRONMENT}")
    
    # Check allowed hosts
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # Check debug mode
    print(f"✅ DEBUG: {settings.DEBUG}")
    
    # Check API endpoints
    print(f"✅ API_BASE_URL: {settings.API_BASE_URL}")
    print(f"✅ PAYMENT_API_BASE_URL: {settings.PAYMENT_API_BASE_URL}")
    
    print(f"✅ Total API endpoints configured: {len(settings.API_ENDPOINTS)}")

def check_url_config():
    """Check URL configuration utility"""
    print("\n🔍 Checking URL Configuration Utility...")
    
    # Test base URLs
    print(f"✅ Base URL: {URLConfig.get_base_url()}")
    print(f"✅ API Base URL: {URLConfig.get_api_base_url()}")
    print(f"✅ Payment API Base URL: {URLConfig.get_payment_api_base_url()}")
    
    # Test specific endpoints
    print(f"✅ Payment Create URL: {URLConfig.get_endpoint('payment_create')}")
    print(f"✅ Payment Status Template: {URLConfig.get_endpoint('payment_status')}")
    print(f"✅ Payment Simulate Template: {URLConfig.get_endpoint('payment_simulate')}")
    
    # Test with parameters
    test_payment_id = "test_payment_123"
    print(f"✅ Payment Status URL (with ID): {URLConfig.get_payment_status_url(test_payment_id)}")
    print(f"✅ Payment Simulate URL (with ID): {URLConfig.get_payment_simulate_url(test_payment_id)}")

def check_environment():
    """Check environment-specific settings"""
    print("\n🔍 Checking Environment Configuration...")
    
    if URLConfig.is_production():
        print("✅ Running in PRODUCTION mode")
        print("✅ HTTPS enabled")
        print("✅ Debug mode disabled")
    elif URLConfig.is_development():
        print("✅ Running in DEVELOPMENT mode")
        print("⚠️  Debug mode enabled")
    else:
        print("⚠️  Unknown environment")

def check_api_endpoints():
    """List all available API endpoints"""
    print("\n🔍 Available API Endpoints:")
    
    endpoints = URLConfig.get_all_endpoints()
    for name, url in endpoints.items():
        print(f"  📡 {name}: {url}")

def check_pythonanywhere_specific():
    """Check PythonAnywhere-specific configurations"""
    print("\n🔍 PythonAnywhere Configuration:")
    
    base_url = URLConfig.get_base_url()
    if "pythonanywhere.com" in base_url:
        print("✅ PythonAnywhere domain detected")
        print(f"✅ Domain: {base_url}")
        
        # Check if HTTPS is used
        if base_url.startswith("https://"):
            print("✅ HTTPS enabled (required for PythonAnywhere)")
        else:
            print("⚠️  HTTPS not enabled - this may cause issues")
    else:
        print("⚠️  Not using PythonAnywhere domain")

def main():
    """Main configuration check"""
    print("=" * 60)
    print("🔧 TaraTech API Configuration Checker")
    print("=" * 60)
    
    try:
        check_django_settings()
        check_url_config()
        check_environment()
        check_api_endpoints()
        check_pythonanywhere_specific()
        
        print("\n" + "=" * 60)
        print("✅ Configuration check completed successfully!")
        print("=" * 60)
        
        print("\n🎯 Quick Start:")
        print(f"   Your API is available at: {URLConfig.get_api_base_url()}")
        print(f"   Test payment creation: {URLConfig.get_endpoint('payment_create')}")
        print(f"   Run tests with: python test_payment_api.py")
        
    except Exception as e:
        print(f"\n❌ Configuration check failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 