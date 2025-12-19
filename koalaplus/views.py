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
def trial_login(request):
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

@api_view(['POST'])
@permission_classes([AllowAny])
def trial_broadcast(request):
    """Trial function to broadcast data. Client handles authentication and sends token."""
    # Get Authorization token from headers (try both Authorization and AUTHORIZATION)
    auth_header = request.headers.get('Authorization') or request.headers.get('AUTHORIZATION')
    if not auth_header:
        return Response({
            "error": "Authorization header is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure Authorization header is in "Bearer {token}" format
    auth_header = auth_header.strip()
    if not auth_header.startswith('Bearer '):
        # Check if it starts with Bearer (case-insensitive) but without proper spacing
        if auth_header.lower().startswith('bearer'):
            # Extract token part after "Bearer" or "bearer"
            token_part = auth_header[6:].strip()  # Remove "Bearer" (6 chars)
            auth_header = f'Bearer {token_part}'
        else:
            # Just the token, add Bearer prefix
            auth_header = f'Bearer {auth_header}'
    
    # Get payload data from request
    # For reservation success, default both campaignName and templateId to "007"
    campaign_name = request.data.get('campaignName', '007')
    notification_data = request.data.get('notificationData', [])
    
    # Validate campaignName
    if not campaign_name:
        return Response({
            "error": "campaignName is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate notificationData
    if not notification_data:
        return Response({
            "error": "notificationData is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not isinstance(notification_data, list):
        return Response({
            "error": "notificationData must be an array"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate each notification data item and normalize phone numbers
    for item in notification_data:
        if not isinstance(item, dict):
            return Response({
                "error": "Each item in notificationData must be an object"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if 'phoneNumber' not in item:
            return Response({
                "error": "phoneNumber is required in each notificationData item"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize phone number - just strip whitespace, don't add + prefix
        item['phoneNumber'] = str(item['phoneNumber']).strip()
        
        # paramData is optional according to docs, but validate if provided
        if 'paramData' in item and not isinstance(item['paramData'], list):
            return Response({
                "error": "paramData must be an array"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Prepare broadcast payload - only include fields that are provided
    broadcast_payload_data = {
        "campaignName": campaign_name,
        "notificationData": notification_data
    }
    
    # Add optional fields if provided
    if 'description' in request.data:
        broadcast_payload_data['description'] = request.data.get('description')
    
    if 'scheduledTime' in request.data:
        broadcast_payload_data['scheduledTime'] = request.data.get('scheduledTime')
    
    broadcast_url = "https://api.koalaapp.id/v1/plus/broadcast/json"
    # Convert payload to JSON string as shown in docs example
    broadcast_payload = json.dumps(broadcast_payload_data, ensure_ascii=False)
    broadcast_headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': auth_header
    }
    
    try:
        # Use data= with JSON string as shown in docs example
        broadcast_response = requests.post(broadcast_url, headers=broadcast_headers, data=broadcast_payload)
        
        # Check status before raising
        if broadcast_response.status_code >= 400:
            # Get error details from response
            response_text = broadcast_response.text or ""
            try:
                error_details = broadcast_response.json()
            except:
                error_details = {
                    "raw_text": response_text,
                    "note": "Response is not valid JSON"
                }
            
            return Response({
                "error": "Failed to broadcast data",
                "message": f"{broadcast_response.status_code} Client Error",
                "status_code": broadcast_response.status_code,
                "api_error_response": error_details,
                "api_response_text": response_text,
                "api_response_headers": dict(broadcast_response.headers),
                "debug_info": {
                    "auth_header_format": "Bearer {token}" if auth_header.startswith("Bearer ") else "Invalid format",
                    "auth_header_length": len(auth_header),
                    "auth_header_preview": auth_header[:50] + "..." if len(auth_header) > 50 else auth_header,
                    "campaign_name": campaign_name,
                    "notification_count": len(notification_data),
                    "payload_sent": broadcast_payload_data,
                    "payload_json_string": broadcast_payload,
                    "payload_length": len(broadcast_payload),
                    "request_url": broadcast_url
                }
            }, status=broadcast_response.status_code)
        
        broadcast_response.raise_for_status()
        return Response(broadcast_response.json(), status=status.HTTP_200_OK)
        
    except requests.exceptions.HTTPError as e:
        # Get more details from the error response
        error_details = {}
        response_text = ""
        response_headers = {}
        status_code = 500
        
        if hasattr(e, 'response') and e.response:
            status_code = getattr(e.response, 'status_code', 500)
            
            # Get response text - try multiple ways to access it
            try:
                response_text = e.response.text or ""
            except:
                try:
                    response_text = str(e.response.content.decode('utf-8', errors='ignore'))
                except:
                    response_text = "Could not read response text"
            
            # Try to parse as JSON
            try:
                if response_text:
                    error_details = e.response.json()
                else:
                    error_details = {"note": "Empty response body"}
            except:
                error_details = {
                    "raw_text": response_text,
                    "note": "Response is not valid JSON"
                }
            
            # Get response headers for debugging
            try:
                if hasattr(e.response, 'headers'):
                    response_headers = dict(e.response.headers)
            except:
                response_headers = {}
        
        # Build comprehensive error response
        error_response = {
            "error": "Failed to broadcast data",
            "message": str(e),
            "status_code": status_code,
            "api_error_response": error_details,
            "api_response_text": response_text,
            "api_response_headers": response_headers,
            "debug_info": {
                "auth_header_format": "Bearer {token}" if auth_header.startswith("Bearer ") else "Invalid format",
                "auth_header_length": len(auth_header),
                "auth_header_preview": auth_header[:50] + "..." if len(auth_header) > 50 else auth_header,
                "campaign_name": campaign_name,
                "notification_count": len(notification_data),
                "payload_sent": broadcast_payload_data,
                "payload_json_string": broadcast_payload,
                "payload_length": len(broadcast_payload),
                "request_url": broadcast_url
            }
        }
        
        return Response(error_response, status=status_code)
    except requests.exceptions.RequestException as e:
        error_status = e.response.status_code if hasattr(e, 'response') and e.response else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({
            "error": "Failed to broadcast data",
            "message": str(e)
        }, status=error_status)
    except Exception as e:
        # Catch any other unexpected exceptions
        return Response({
            "error": "Unexpected error occurred",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def broadcast_reservation_success(request):
    """Broadcast successful reservation notification. Token is received in request body."""
    # Get token from request body
    token = request.data.get('token')
    if not token:
        return Response({
            "error": "token is required in request body"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Format token as Authorization header for Koala API
    token = str(token).strip()
    # Remove "Bearer " prefix if already present, then add it back
    if token.lower().startswith('bearer'):
        token = token[6:].strip()  # Remove "Bearer" (6 chars)
    auth_header = f'Bearer {token}'
    
    # Get payload data from request
    campaign_name = request.data.get('campaignName', '002')
    notification_data = request.data.get('notificationData', [])
    template_id = request.data.get('templateId', '007')
    
    # Validate campaignName
    if not campaign_name:
        return Response({
            "error": "campaignName is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate templateId
    if not template_id:
        return Response({
            "error": "templateId is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate notificationData
    if not notification_data:
        return Response({
            "error": "notificationData is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not isinstance(notification_data, list):
        return Response({
            "error": "notificationData must be an array"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate each notification data item and normalize phone numbers
    for item in notification_data:
        if not isinstance(item, dict):
            return Response({
                "error": "Each item in notificationData must be an object"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if 'phoneNumber' not in item:
            return Response({
                "error": "phoneNumber is required in each notificationData item"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize phone number - ensure it includes + and country code
        phone_number = str(item['phoneNumber']).strip()
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        item['phoneNumber'] = phone_number
        
        # paramData is optional according to docs, but validate if provided
        if 'paramData' in item and not isinstance(item['paramData'], list):
            return Response({
                "error": "paramData must be an array"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Prepare broadcast payload - include templateId
    broadcast_payload_data = {
        "campaignName": campaign_name,
        "templateId": template_id,
        "description": request.data.get('description'),
        "notificationData": notification_data
    }
    
    # Add optional fields if provided
    if 'description' in request.data:
        broadcast_payload_data['description'] = request.data.get('description')
    
    if 'scheduledTime' in request.data:
        broadcast_payload_data['scheduledTime'] = request.data.get('scheduledTime')
    
    broadcast_url = "https://api.koalaapp.id/v1/plus/broadcast/json"
    # Convert payload to JSON string as shown in docs example
    broadcast_payload = json.dumps(broadcast_payload_data, ensure_ascii=False)
    broadcast_headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': auth_header
    }
    
    try:
        # Use data= with JSON string as shown in docs example
        broadcast_response = requests.post(broadcast_url, headers=broadcast_headers, data=broadcast_payload)
        
        # Check status before raising
        if broadcast_response.status_code >= 400:
            # Get error details from response
            response_text = broadcast_response.text or ""
            try:
                error_details = broadcast_response.json()
            except:
                error_details = {
                    "raw_text": response_text,
                    "note": "Response is not valid JSON"
                }
            
            return Response({
                "error": "Failed to broadcast reservation success",
                "message": f"{broadcast_response.status_code} Client Error",
                "status_code": broadcast_response.status_code,
                "api_error_response": error_details,
                "api_response_text": response_text,
                "api_response_headers": dict(broadcast_response.headers),
                "debug_info": {
                    "auth_header_format": "Bearer {token}" if auth_header.startswith("Bearer ") else "Invalid format",
                    "auth_header_length": len(auth_header),
                    "auth_header_preview": auth_header[:50] + "..." if len(auth_header) > 50 else auth_header,
                    "campaign_name": campaign_name,
                    "template_id": template_id,
                    "notification_count": len(notification_data),
                    "payload_sent": broadcast_payload_data,
                    "payload_json_string": broadcast_payload,
                    "payload_length": len(broadcast_payload),
                    "request_url": broadcast_url
                }
            }, status=broadcast_response.status_code)
        
        broadcast_response.raise_for_status()
        return Response(broadcast_response.json(), status=status.HTTP_200_OK)
        
    except requests.exceptions.HTTPError as e:
        # Get more details from the error response
        error_details = {}
        response_text = ""
        response_headers = {}
        status_code = 500
        
        if hasattr(e, 'response') and e.response:
            status_code = getattr(e.response, 'status_code', 500)
            
            # Get response text - try multiple ways to access it
            try:
                response_text = e.response.text or ""
            except:
                try:
                    response_text = str(e.response.content.decode('utf-8', errors='ignore'))
                except:
                    response_text = "Could not read response text"
            
            # Try to parse as JSON
            try:
                if response_text:
                    error_details = e.response.json()
                else:
                    error_details = {"note": "Empty response body"}
            except:
                error_details = {
                    "raw_text": response_text,
                    "note": "Response is not valid JSON"
                }
            
            # Get response headers for debugging
            try:
                if hasattr(e.response, 'headers'):
                    response_headers = dict(e.response.headers)
            except:
                response_headers = {}
        
        # Build comprehensive error response
        error_response = {
            "error": "Failed to broadcast reservation success",
            "message": str(e),
            "status_code": status_code,
            "api_error_response": error_details,
            "api_response_text": response_text,
            "api_response_headers": response_headers,
            "debug_info": {
                "auth_header_format": "Bearer {token}" if auth_header.startswith("Bearer ") else "Invalid format",
                "auth_header_length": len(auth_header),
                "auth_header_preview": auth_header[:50] + "..." if len(auth_header) > 50 else auth_header,
                "campaign_name": campaign_name,
                "template_id": template_id,
                "notification_count": len(notification_data),
                "payload_sent": broadcast_payload_data,
                "payload_json_string": broadcast_payload,
                "payload_length": len(broadcast_payload),
                "request_url": broadcast_url
            }
        }
        
        return Response(error_response, status=status_code)
    except requests.exceptions.RequestException as e:
        error_status = e.response.status_code if hasattr(e, 'response') and e.response else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response({
            "error": "Failed to broadcast reservation success",
            "message": str(e)
        }, status=error_status)
    except Exception as e:
        # Catch any other unexpected exceptions
        return Response({
            "error": "Unexpected error occurred",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)