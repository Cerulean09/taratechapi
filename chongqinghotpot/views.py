from django.http import JsonResponse
import os
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timezone


def generate_headers(method: str, path: str):
    """
    Generate headers for Mekari (Qontak) API request.
    Includes both HMAC signature and Bearer access token.
    """

    # Current UTC time in RFC 7231 format
    dt = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Build signing string (for HMAC)
    request_line = f"{method.upper()} {path} HTTP/1.1"
    signing_string = f"date: {dt}\n{request_line}"

    # Load credentials from environment variables
    client_id = os.getenv("CQ_HOTPOT_QONTAK_CLIENT_ID")
    client_secret = os.getenv("CQ_HOTPOT_QONTAK_CLIENT_SECRET")
    sso_id = os.getenv("CQ_HOTPOT_QONTAK_SSO_ID")
    access_token = os.getenv("CQ_HOTPOT_QONTAK_ACCESS_TOKEN")

    if not client_id or not client_secret or not access_token:
        raise Exception("Missing Mekari credentials (client ID, secret, or access token)")

    # Generate HMAC-SHA256 signature
    signature = base64.b64encode(
        hmac.new(
            client_secret.encode(),
            signing_string.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    # Mekari requires both Bearer + HMAC
    hmac_signature = (
        f'hmac username="{client_id}", algorithm="hmac-sha256", '
        f'headers="date request-line", signature="{signature}"'
    )

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Date": dt,
        "Authorization": f"Bearer {access_token}",  # OAuth2 token
        "X-Mekari-Signature": hmac_signature,       # HMAC signature
    }

    # Some endpoints require user context
    if sso_id:
        headers["X-Crm-User-Sso-Id"] = sso_id

    return headers


def send_mekari_request(method: str, path: str, payload=None):
    """
    Send a signed Mekari API request and return the parsed response.
    """
    base_url = os.getenv("MEKARI_URL", "api.mekari.com")
    url = f"https://{base_url}{path}"

    headers = generate_headers(method, path)

    try:
        resp = requests.request(method.upper(), url, headers=headers, json=payload)
        body = resp.json() if resp.content else {}
        return {"http_code": resp.status_code, "body": body}
    except Exception as e:
        return {"http_code": 500, "body": {"error": str(e)}}


def get_all_contacts(request):
    """
    Retrieve all contacts from Qontak (Mekari) API.
    """
    path = "/qontak/chat/v1/contacts"  # uses your current scope (qontak-chat:contacts:list)
    result = send_mekari_request("GET", path)

    if result["http_code"] != 200:
        print("Failed to fetch contacts:", result)
        return JsonResponse(result, status=result["http_code"], safe=False)

    return JsonResponse(result["body"], safe=False)
