import hmac
import hashlib
import base64
import requests
import json
from datetime import datetime, timezone
import time
import os
import uuid
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.cache import cache
from urllib.parse import urlencode
from django.utils import timezone as django_timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import supabase
from supabase import create_client, Client, ClientOptions

# --------------------------
# CONFIG
# --------------------------
CLIENT_ID = os.getenv('CQ_HOTPOT_QONTAK_CLIENT_ID')
CLIENT_SECRET = os.getenv('CQ_HOTPOT_QONTAK_CLIENT_SECRET')
CRM_CLIENT_ID = os.getenv('CQ_HOTPOT_QONTAK_CRM_CLIENT_ID')
CRM_CLIENT_SECRET = os.getenv('CQ_HOTPOT_QONTAK_CRM_CLIENT_SECRET')
CQ_HOTPOT_QONTAK_CRM_REDIRECT_URI = os.getenv('CQ_HOTPOT_QONTAK_CRM_REDIRECT_URI')
BASE_URL = os.getenv('MEKARI_URL_PRODUCTION', 'https://api.mekari.com')
CQ_HOTPOT_QONTAK_CRM_BASE_URL = os.getenv('CQ_HOTPOT_QONTAK_CRM_BASE_URL', 'https://app.qontak.com')
CQ_HOTPOT_QONTAK_CRM_TOKEN_URL = os.getenv('CQ_HOTPOT_QONTAK_CRM_TOKEN_URL', 'https://app.qontak.com/oauth/token')
CQ_HOTPOT_QONTAK_CRM_AUTHORIZE_URL = os.getenv('CQ_HOTPOT_QONTAK_CRM_AUTHORIZE_URL', 'https://app.qontak.com/oauth/authorize')

# Token cache keys for CRM OAuth tokens (using Django cache framework)
CRM_TOKEN_CACHE_KEY = 'crm_oauth_access_token'
CRM_REFRESH_TOKEN_CACHE_KEY = 'crm_oauth_refresh_token'
CRM_TOKEN_EXPIRES_AT_KEY = 'crm_oauth_expires_at'


# --------------------------
# HEADER GENERATOR
# --------------------------
def generate_headers(method: str, path: str, client_id: str, client_secret: str):
    """
    Generate HMAC authentication headers for Mekari Qontak API.
    Equivalent to the PHP example's generate_headers().
    """
    # RFC 7231 (GMT) date format
    datetime_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Canonical request line
    request_line = method.upper() + " " + path + " HTTP/1.1"

    # Signing string: "date: <date>\n<method> <path> HTTP/1.1"
    signing_string = "date: " + datetime_str + "\n" + request_line

    # HMAC-SHA256 digest and Base64 encode
    digest_bytes = hmac.new(
        client_secret.encode("utf-8"),
        signing_string.encode("utf-8"),
        hashlib.sha256
    ).digest()
    signature = base64.b64encode(digest_bytes).decode("utf-8")

    # Final Authorization header
    authorization = (
        'hmac username="' + client_id + '", '
        'algorithm="hmac-sha256", '
        'headers="date request-line", '
        'signature="' + signature + '"'
    )

    return {
        "Authorization": authorization,
        "Date": datetime_str,
        "Content-Type": "application/json"
    }


# --------------------------
# REQUEST FUNCTION
# --------------------------
def send_mekari_request(method: str, path: str, payload: dict = None, client_id: str = CLIENT_ID, client_secret: str = CLIENT_SECRET):
    """
    Send a signed request to Mekari API (GET or POST).
    Equivalent to the PHP send_mekari_request() function.
    """
    url = BASE_URL.rstrip('/') + path
    headers = generate_headers(method, path, client_id, client_secret)

    if method.upper() == "POST":
        response = requests.post(url, headers=headers, json=payload)
    elif method.upper() == "GET":
        response = requests.get(url, headers=headers, params=payload)
    else:
        response = requests.request(method.upper(), url, headers=headers, json=payload)

    try:
        body = response.json()
    except Exception:
        body = response.text

    return {
        "http_code": response.status_code,
        "response": body
    }


# --------------------------
# CRM OAUTH TOKEN MANAGEMENT
# --------------------------
def exchange_authorization_code_for_token(authorization_code):
    """
    Exchange authorization code for access token using OAuth Authorization Code flow.
    
    Args:
        authorization_code: The authorization code received from OAuth callback
    
    Returns:
        Dictionary with access_token, refresh_token, expires_at
    """
    if not CRM_CLIENT_ID or not CRM_CLIENT_SECRET or not CQ_HOTPOT_QONTAK_CRM_REDIRECT_URI:
        raise Exception("CRM_CLIENT_ID, CRM_CLIENT_SECRET, and CQ_HOTPOT_QONTAK_CRM_REDIRECT_URI environment variables must be set")
    
    url = CQ_HOTPOT_QONTAK_CRM_TOKEN_URL
    
    payload = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'client_id': CRM_CLIENT_ID,
        'client_secret': CRM_CLIENT_SECRET,
        'redirect_uri': CQ_HOTPOT_QONTAK_CRM_REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code != 200:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json
            except:
                pass
            
            payload_info = {
                'grant_type': payload['grant_type'],
                'code': '***MASKED***',
                'client_id': payload['client_id'],
                'client_secret': '***MASKED***',
                'redirect_uri': payload['redirect_uri']
            }
            
            raise Exception(f"Failed to exchange authorization code: {response.status_code} - {error_detail}. Request payload: {payload_info}")
        
        token_data = response.json()
        
        if 'access_token' not in token_data:
            raise Exception(f"Invalid token response: access_token not found. Response: {token_data}")
        
        # Cache the token data using Django cache (expires in 1 day to be safe)
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
        expires_at = time.time() + expires_in
        
        # Store tokens in cache (cache for 24 hours to ensure persistence)
        try:
            cache.set(CRM_TOKEN_CACHE_KEY, access_token, timeout=86400)
            cache.set(CRM_REFRESH_TOKEN_CACHE_KEY, refresh_token, timeout=86400)
            cache.set(CRM_TOKEN_EXPIRES_AT_KEY, expires_at, timeout=86400)
            
            # Verify tokens were saved
            saved_access_token = cache.get(CRM_TOKEN_CACHE_KEY)
            saved_refresh_token = cache.get(CRM_REFRESH_TOKEN_CACHE_KEY)
            saved_expires_at = cache.get(CRM_TOKEN_EXPIRES_AT_KEY)
            
            if not saved_access_token or not saved_refresh_token or not saved_expires_at:
                raise Exception(f"Failed to save tokens to cache. Saved: access_token={saved_access_token is not None}, refresh_token={saved_refresh_token is not None}, expires_at={saved_expires_at is not None}")
        except Exception as cache_error:
            raise Exception(f"Cache error while saving tokens: {str(cache_error)}")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        }
    except Exception as e:
        raise Exception(f"Failed to exchange authorization code: {str(e)}")


def refresh_crm_access_token():
    """
    Refresh the access token using refresh_token.
    
    Returns:
        Access token string
    """
    refresh_token = cache.get(CRM_REFRESH_TOKEN_CACHE_KEY)
    
    if not refresh_token:
        raise Exception("No refresh token available. Please re-authenticate via /crm/login/")
    
    if not CRM_CLIENT_ID or not CRM_CLIENT_SECRET:
        raise Exception("CRM_CLIENT_ID and CRM_CLIENT_SECRET environment variables must be set")
    
    url = CQ_HOTPOT_QONTAK_CRM_TOKEN_URL
    
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CRM_CLIENT_ID,
        'client_secret': CRM_CLIENT_SECRET
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code != 200:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json
            except:
                pass
            
            payload_info = {
                'grant_type': payload['grant_type'],
                'refresh_token': '***MASKED***',
                'client_id': payload['client_id'],
                'client_secret': '***MASKED***'
            }
            
            raise Exception(f"Failed to refresh token: {response.status_code} - {error_detail}. Request payload: {payload_info}")
        
        token_data = response.json()
        
        if 'access_token' not in token_data:
            raise Exception(f"Invalid token response: access_token not found. Response: {token_data}")
        
        # Update cache
        access_token = token_data.get('access_token')
        new_refresh_token = token_data.get('refresh_token', refresh_token)  # Use new refresh token if provided, otherwise keep old one
        expires_in = token_data.get('expires_in', 3600)
        expires_at = time.time() + expires_in
        
        # Store tokens in cache (cache for 24 hours to ensure persistence)
        cache.set(CRM_TOKEN_CACHE_KEY, access_token, timeout=86400)
        cache.set(CRM_REFRESH_TOKEN_CACHE_KEY, new_refresh_token, timeout=86400)
        cache.set(CRM_TOKEN_EXPIRES_AT_KEY, expires_at, timeout=86400)
        
        return access_token
    except Exception as e:
        raise Exception(f"Failed to refresh token: {str(e)}")


def get_crm_oauth_token(force_refresh=False):
    """
    Get OAuth access token for CRM API.
    Automatically refreshes token if expired.
    Uses cached token if still valid.
    
    Args:
        force_refresh: If True, force a token refresh even if cached token exists
    
    Returns:
        Access token string
    
    Raises:
        Exception: If no token is available (user needs to authenticate via /crm/login/)
    """
    # Check if we have a valid cached token
    if not force_refresh:
        access_token = cache.get(CRM_TOKEN_CACHE_KEY)
        expires_at = cache.get(CRM_TOKEN_EXPIRES_AT_KEY)
        
        if access_token and expires_at:
            # Check if token is still valid (with 60 second buffer)
            if time.time() < (expires_at - 60):
                return access_token
            
            # Token expired, try to refresh
            refresh_token = cache.get(CRM_REFRESH_TOKEN_CACHE_KEY)
            if refresh_token:
                try:
                    return refresh_crm_access_token()
                except Exception as e:
                    # Refresh failed, need to re-authenticate
                    raise Exception(f"Token expired and refresh failed: {str(e)}. Please re-authenticate via /api/chongqinghotpot/crm/login/")
    
    # No valid token available
    raise Exception("No valid access token. Please authenticate first by visiting /api/chongqinghotpot/crm/login/")


# --------------------------
# CRM REQUEST FUNCTION
# --------------------------
def send_mekari_crm_request(method: str, path: str, params: dict = None, payload: dict = None):
    """
    Send a request to Mekari CRM API using OAuth Bearer token authentication.
    Automatically loads cached access_token and refreshes when expired.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: API path (e.g., '/api/v3.1/contacts')
        params: Query parameters for GET requests
        payload: Request body for POST requests
    
    Returns:
        Dictionary with 'http_code' and 'response' keys
    
    Raises:
        Exception: If token is not available (user needs to authenticate via /crm/login/)
    """
    # Get OAuth token (automatically refreshes if expired)
    try:
        access_token = get_crm_oauth_token()
    except Exception as e:
        # Re-raise with request context
        request_info = {
            "method": method,
            "path": path,
            "params": params,
            "payload": payload
        }
        raise Exception(f"{str(e)}. CRM API request info: {request_info}")
    
    url = f"{CQ_HOTPOT_QONTAK_CRM_BASE_URL}{path}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    if method.upper() == "POST":
        response = requests.post(url, headers=headers, json=payload, params=params)
    elif method.upper() == "GET":
        response = requests.get(url, headers=headers, params=params)
    else:
        response = requests.request(method.upper(), url, headers=headers, json=payload, params=params)
    
    try:
        body = response.json()
    except Exception:
        body = response.text
    
    return {
        "http_code": response.status_code,
        "response": body
    }


# --------------------------
# CRM OAUTH FLOW VIEWS
# --------------------------
def crm_login(request):
    """
    Redirect user to Qontak OAuth authorization page.
    GET /api/chongqinghotpot/crm/login/
    """
    if not CRM_CLIENT_ID or not CQ_HOTPOT_QONTAK_CRM_REDIRECT_URI:
        return JsonResponse({
            "error": "CRM_CLIENT_ID and CQ_HOTPOT_QONTAK_CRM_REDIRECT_URI environment variables must be set"
        }, status=500)
    
    # Build authorization URL
    auth_url = CQ_HOTPOT_QONTAK_CRM_AUTHORIZE_URL
    params = {
        'client_id': CRM_CLIENT_ID,
        'redirect_uri': CQ_HOTPOT_QONTAK_CRM_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'crm'
    }
    
    authorization_url = f"{auth_url}?{urlencode(params)}"
    
    # Redirect to Qontak authorization page
    return HttpResponseRedirect(authorization_url)


def crm_callback(request):
    """
    Handle OAuth callback from Qontak.
    Receives authorization code and exchanges it for access token.
    GET /api/chongqinghotpot/crm/callback/?code=xxxx
    """
    try:
        # Extract authorization code from query parameters
        authorization_code = request.GET.get('code')
        
        if not authorization_code:
            error = request.GET.get('error', 'Unknown error')
            error_description = request.GET.get('error_description', '')
            return JsonResponse({
                "error": f"Authorization failed: {error}",
                "error_description": error_description
            }, status=400)
        
        # Exchange authorization code for access token
        token_data = exchange_authorization_code_for_token(authorization_code)
        
        # Verify tokens are in cache after saving
        access_token_check = cache.get(CRM_TOKEN_CACHE_KEY)
        refresh_token_check = cache.get(CRM_REFRESH_TOKEN_CACHE_KEY)
        expires_at_check = cache.get(CRM_TOKEN_EXPIRES_AT_KEY)
        
        return JsonResponse({
            "message": "Successfully authenticated with Qontak CRM",
            "token_acquired": True,
            "expires_at": datetime.fromtimestamp(token_data['expires_at']).isoformat(),
            "access_token_preview": token_data['access_token'][:20] + "..." if token_data.get('access_token') else None,
            "cache_verification": {
                "access_token_saved": access_token_check is not None,
                "refresh_token_saved": refresh_token_check is not None,
                "expires_at_saved": expires_at_check is not None
            }
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "error_type": type(e).__name__
        }, status=500)


def crm_token_status(request):
    """
    Check the status of the cached CRM OAuth token.
    Useful for debugging token persistence issues.
    GET /api/chongqinghotpot/crm/token-status/
    """
    # Test if cache is working at all
    test_key = 'crm_cache_test'
    test_value = 'test_' + str(time.time())
    cache.set(test_key, test_value, timeout=60)
    cache_test_result = cache.get(test_key)
    cache_working = cache_test_result == test_value
    
    access_token = cache.get(CRM_TOKEN_CACHE_KEY)
    refresh_token = cache.get(CRM_REFRESH_TOKEN_CACHE_KEY)
    expires_at = cache.get(CRM_TOKEN_EXPIRES_AT_KEY)
    
    current_time = time.time()
    is_valid = False
    time_until_expiry = None
    
    if access_token and expires_at:
        time_until_expiry = expires_at - current_time
        is_valid = time_until_expiry > 60  # Valid if more than 60 seconds remaining
    
    return JsonResponse({
        "cache_working": cache_working,
        "cache_test": {
            "set_value": test_value,
            "retrieved_value": cache_test_result,
            "match": cache_working
        },
        "has_access_token": access_token is not None,
        "has_refresh_token": refresh_token is not None,
        "has_expires_at": expires_at is not None,
        "is_valid": is_valid,
        "expires_at": datetime.fromtimestamp(expires_at).isoformat() if expires_at else None,
        "time_until_expiry_seconds": round(time_until_expiry, 2) if time_until_expiry is not None else None,
        "current_time": datetime.fromtimestamp(current_time).isoformat(),
        "access_token_preview": access_token[:20] + "..." if access_token else None
    }, status=200)


def get_all_whatsapp_templates(request):
    response = send_mekari_request("GET", "/qontak/chat/v1/templates/whatsapp", {})

    # response is a dict with 'http_code' and 'response' keys
    http_code = response.get('http_code', 200)
    response_data = response.get('response', {})

    # response_data is already parsed (either dict or string)
    if isinstance(response_data, dict):
        data = response_data
    else:
        # If it's a string, wrap it
        data = {"raw": response_data}

    return JsonResponse(data, status=http_code)


def get_all_rooms(request):
    response = send_mekari_request("GET", "/qontak/chat/v1/rooms", {})

    # response is a dict with 'http_code' and 'response' keys
    http_code = response.get('http_code', 200)
    response_data = response.get('response', {})

    # response_data is already parsed (either dict or string)
    if isinstance(response_data, dict):
        data = response_data
    else:
        # If it's a string, wrap it
        data = {"raw": response_data}

    return JsonResponse(data, status=http_code)

def create_cq_hotpot_supabase_client() -> Client:
    """Create Supabase client for Chongqing Hotpot using CQ_HOTPOT_SUPABASE credentials."""
    url = os.getenv('CQ_HOTPOT_SUPABASE_CLIENT_URL')
    key = os.getenv('CQ_HOTPOT_SUPABASE_CLIENT_SECRET')
    if not url or not key:
        raise Exception("CQ_HOTPOT_SUPABASE_CLIENT_URL and CQ_HOTPOT_SUPABASE_CLIENT_SECRET environment variables must be set")
    return create_client(url, key, options=ClientOptions())

def set_message_interaction_settings(request):
    pass

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def handle_message_interaction_webhook(request):
    """
    Handle webhook from Qontak for message interactions.
    Receives webhook data and uploads it to Supabase table 'qontak_message_interactions'.
    
    Expected data structure:
    {
        "id": "string",
        "type": "string",
        "room_id": "string",
        ...
    }
    
    Maps to Supabase model:
    - id: UUID v1 (String)
    - createdAt: DateTime
    - rawJson: Map<String, dynamic> (entire response from qontak)
    - type: String (from response)
    - utcOffset: number (default 0)
    """
    try:
        # Handle GET requests (webhook verification)
        if request.method == 'GET':
            return JsonResponse({
                "message": "Webhook endpoint is active",
                "status": "ok"
            }, status=200)
        
        # Get webhook data from request (POST)
        webhook_data = request.data if hasattr(request, 'data') else {}
        
        # # If data is empty, try to get from request body
        # if not webhook_data:
        #     try:
        #         if request.body:
        #             webhook_data = json.loads(request.body)
        #     except (json.JSONDecodeError, AttributeError):
        #         pass
        
        if not webhook_data:
            # Treat as verification ping / empty event
            return JsonResponse({"status": "ok"}, status=200)
        
        

        
        # Extract type from webhook data
        message_type = webhook_data.get('type', '')
        
        # Generate UUID v1 for the id
        record_id = str(uuid.uuid1())
        
        # Get current datetime in UTC (since running on fly.io with UTC time)
        current_datetime = datetime.now(timezone.utc)
        
        # Prepare data for Supabase
        print('Saving message interaction to database... 0')
        supabase_data = {
            'id': record_id,
            'createdAt': current_datetime.isoformat(),
            'rawJson': webhook_data,  # Store entire webhook data as JSON
            'type': message_type,
            'utcOffset': 0  # Default to 0 since running on fly.io with UTC time
        }
        
        # Create Supabase client and insert data
        print('Saving message interaction to database... 1')
        supabase_client = create_cq_hotpot_supabase_client()
        print('Saving message interaction to database... 2')
        try:
            response = supabase_client.table('qontak_message_interactions').insert(supabase_data).execute()
        except Exception as e:
            print('Error saving message interaction to database...')
            print(e)
            return JsonResponse({
                "error": "Failed to save message interaction",
                "response": str(e)
            }, status=500)
            
        print('Saving message interaction to database... 3')
        if response.data:
            print('Successfully saved message interaction to database')
            return JsonResponse({
                "message": "Message interaction saved successfully",
                "id": record_id,
                "type": message_type,
                "created_at": current_datetime.isoformat()
            }, status=201)
        else:
            return JsonResponse({
                "error": "Failed to save message interaction",
                "response": str(response)
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "error_type": type(e).__name__
        }, status=500)

def get_all_contacts(request):
    """
    Get all contacts from CRM API.
    Supports optional query parameters: name, job_title, phone, email, 
    crm_company_id, crm_deal_id, crm_status_id, page, per_page
    """
    # Get query parameters from request
    params = {}
    optional_params = ['name', 'job_title', 'phone', 'email', 'crm_company_id', 
                      'crm_deal_id', 'crm_status_id', 'page', 'per_page']
    
    for param in optional_params:
        value = request.GET.get(param)
        if value is not None:
            params[param] = value
    
    try:
        # Use CRM request function with OAuth token
        response = send_mekari_crm_request("GET", "/api/v3.1/contacts", params=params)

        # response is a dict with 'http_code' and 'response' keys
        if not response:
            return JsonResponse({
                "error": "No response from CRM API",
                "request_payload": {
                    "method": "GET",
                    "path": "/api/v3.1/contacts",
                    "params": params
                }
            }, status=500)
        
        http_code = response.get('http_code', 200)
        response_data = response.get('response')

        # Handle None response
        if response_data is None:
            response_data = {}

        # response_data is already parsed (either dict, list, or string)
        if isinstance(response_data, dict):
            data = response_data
        elif isinstance(response_data, list):
            # If it's a list, wrap it in a data key
            data = {"data": response_data}
        elif isinstance(response_data, str):
            # If it's a string, try to parse as JSON, otherwise wrap it
            try:
                data = json.loads(response_data)
            except (json.JSONDecodeError, ValueError):
                data = {"raw": response_data}
        else:
            # Handle other types
            data = {"data": response_data}

        return JsonResponse(data, status=http_code, safe=False)
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "error_type": type(e).__name__,
            "request_payload": {
                "method": "GET",
                "path": "/api/v3.1/contacts",
                "params": params
            }
        }, status=500)


def save_message_interaction_to_db(request):
    """
    Save message interaction to database.
    POST /api/chongqinghotpot/save-message-interaction-to-db/
    """
    
    return JsonResponse({"message": "Message interaction saved to database"}, status=200)

    """
    Test endpoint for handle_message_interaction_webhook.
    Tests uploading to Supabase with sample data.
    GET or POST /api/chongqinghotpot/test-handle-message-interaction-webhook/
    """
    try:
        # Create test webhook data with rawJson = {"text":"this works well"}
        test_webhook_data = {
            "text": "this works well"
        }
        
        # Extract type from test data (or use default)
        message_type = test_webhook_data.get('type', 'test')
        
        # Generate UUID v1 for the id
        record_id = str(uuid.uuid1())
        
        # Get current datetime in UTC (since running on fly.io with UTC time)
        current_datetime = datetime.now(timezone.utc)
        
        # Prepare data for Supabase
        supabase_data = {
            'id': record_id,
            'createdAt': current_datetime.isoformat(),
            'rawJson': test_webhook_data,  # Store test data as JSON
            'type': message_type,
            'utcOffset': 0  # Default to 0 since running on fly.io with UTC time
        }
        
        # Create Supabase client and insert data
        supabase_client = create_cq_hotpot_supabase_client()
        response = supabase_client.table('qontak_message_interactions').insert(supabase_data).execute()
        
        if response.data:
            return JsonResponse({
                "message": "Test message interaction saved successfully",
                "id": record_id,
                "type": message_type,
                "created_at": current_datetime.isoformat(),
                "rawJson": test_webhook_data,
                "supabase_response": response.data[0] if response.data else None
            }, status=201)
        else:
            return JsonResponse({
                "error": "Failed to save test message interaction",
                "response": str(response),
                "supabase_data": supabase_data
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "error_type": type(e).__name__
        }, status=500)