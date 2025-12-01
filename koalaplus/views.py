from django.shortcuts import render
import requests
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def trail_login(request):
    """Trial login function with hardcoded credentials for testing."""
    trial_email = 'robin.dartanto@taratech.id'
    trial_password = 'TaraTech123'
    
    url = "https://api.koalaapp.id/v1/identity/auth/koala-plus/login"
    payload = json.dumps({
        "email": trial_email,
        "password": trial_password
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return Response(response.json(), status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        error_status = e.response.status_code if hasattr(e, 'response') and e.response else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({
            "error": "Failed to login",
            "message": str(e)
        }, status=error_status)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_koala_plus(request):
    """Login to Koala Plus with user credentials."""
    user_email = request.data.get('user_email')
    user_password = request.data.get('user_password')
    
    if not user_email or not user_password:
        return Response({
            "error": "Email and password are required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    url = "https://api.koalaapp.id/v1/identity/auth/koala-plus/login"
    payload = json.dumps({
        "email": user_email,
        "password": user_password
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return Response(response.json(), status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        error_status = e.response.status_code if hasattr(e, 'response') and e.response else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({
            "error": "Failed to login",
            "message": str(e)
        }, status=error_status)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_access_token(request):
    """Refresh the Koala Plus access token using refresh token."""
    koala_refresh_token = request.data.get('koalaRefreshToken')
    
    if not koala_refresh_token:
        return Response({
            "error": "koalaRefreshToken is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    url = "https://api.koalaapp.id/v1/identity/auth/koala-plus/refresh-access"
    payload = json.dumps({
        "koalaRefreshToken": koala_refresh_token
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Check if authorization token is provided in request headers
    auth_header = request.headers.get('Authorization')
    if auth_header:
        headers['Authorization'] = auth_header
    else:
        headers['Authorization'] = 'Bearer '
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return Response(response.json(), status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        error_status = e.response.status_code if hasattr(e, 'response') and e.response else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({
            "error": "Failed to refresh access token",
            "message": str(e)
        }, status=error_status)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_broadcast_templates(request):
    """Get all broadcast templates from Koala Plus."""
    url = "https://api.koalaapp.id/v1/plus/broadcast/template/list"
    headers = {}
    
    # Check if authorization token is provided in request headers
    auth_header = request.headers.get('Authorization')
    if auth_header:
        headers['Authorization'] = auth_header
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return Response(response.json(), status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        error_status = e.response.status_code if hasattr(e, 'response') and e.response else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({
            "error": "Failed to get broadcast templates",
            "message": str(e)
        }, status=error_status)

@api_view(['POST'])
@permission_classes([AllowAny])
def broadcast_otp(request):
    """Broadcast OTP to a phone number via Koala Plus."""
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({
            "error": "phone_number is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure phone number starts with +
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    # Get optional parameters with defaults
    campaign_name = request.data.get('campaignName', 'OPW')
    code = request.data.get('code', 123456)
    code_length = request.data.get('codeLength', 6)
    code_validity = request.data.get('codeValidity', 30)
    otp_type = request.data.get('type', 'SELF_VALIDATION')
    
    url = "https://api.koalaapp.id/v1/plus/broadcast/otp"
    payload = json.dumps({
        "destination": phone_number,
        "campaignName": campaign_name,
        "code": code,
        "codeLength": code_length,
        "codeValidity": code_validity,
        "type": otp_type
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Check if kokatto token is provided in request headers
    kokatto_token = request.headers.get('x-kokatto-token')
    if kokatto_token:
        headers['x-kokatto-token'] = kokatto_token
    else:
        headers['x-kokatto-token'] = 'Bearer '
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return Response(response.json(), status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        error_status = e.response.status_code if hasattr(e, 'response') and e.response else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({
            "error": "Failed to broadcast OTP",
            "message": str(e)
        }, status=error_status)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def trial_get_broadcast_templates(request):
    """Trial function that calls trail_login first, then gets broadcast templates."""
    # Step 1: Perform trial login
    trial_email = 'robin.dartanto@taratech.id'
    trial_password = 'TaraTech123'
    
    login_url = "https://api.koalaapp.id/v1/identity/auth/koala-plus/login"
    login_payload = json.dumps({
        "email": trial_email,
        "password": trial_password
    })
    login_headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        # Login to get access token
        login_response = requests.post(login_url, headers=login_headers, data=login_payload)
        login_response.raise_for_status()
        login_data = login_response.json()
        
        # Extract access token from response
        # Response structure: { "statusCode": 200, "statusMessage": "OK", "data": { "koalaToken": { "accessToken": "..." } } }
        access_token = None
        if login_data.get('data') and login_data['data'].get('koalaToken'):
            access_token = login_data['data']['koalaToken'].get('accessToken')
        
        if not access_token:
            return Response({
                "error": "Failed to extract access token from login response",
                "login_response": login_data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Step 2: Get broadcast templates using the access token
        templates_url = "https://api.koalaapp.id/v1/plus/broadcast/template/list"
        templates_headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        templates_response = requests.get(templates_url, headers=templates_headers)
        templates_response.raise_for_status()
        
        return Response({
            "login_status": "success",
            "access_token_obtained": True,
            "broadcast_templates": templates_response.json()
        }, status=status.HTTP_200_OK)
        
    except requests.exceptions.RequestException as e:
        error_status = e.response.status_code if hasattr(e, 'response') and e.response else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({
            "error": "Failed to get broadcast templates",
            "message": str(e),
            "step": "login" if "login" in str(e).lower() or login_url in str(e) else "get_templates"
        }, status=error_status)