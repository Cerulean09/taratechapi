import os
import hmac
import hashlib
import base64
from datetime import datetime, timezone

import requests
from django.http import JsonResponse

def generate_hmac_headers(method: str, path: str, query_string: str = ""):
    """
    Generates HMAC headers for Mekari (Qontak) API authentication.
    Equivalent to the Postman Pre-Request Script using CryptoJS.

    Args:
        method (str): HTTP method (GET, POST, etc.)
        path (str): The request path (e.g. "/qontak/chat/v1/contacts/...")
        query_string (str, optional): URL query string (e.g. "page=2&limit=100")

    Returns:
        dict: Headers including Authorization, Date, and Content-Type
    """

    # ✅ Load credentials from environment (set in PythonAnywhere web settings)
    client_id = os.getenv("CQ_HOTPOT_QONTAK_CLIENT_ID")
    client_secret = os.getenv("CQ_HOTPOT_QONTAK_CLIENT_SECRET")
    # sso_id = os.getenv("CQ_HOTPOT_QONTAK_SSO_ID")  # optional, required for user-specific requests

    if not client_id or not client_secret:
        raise ValueError("Missing Mekari CLIENT_ID or CLIENT_SECRET environment variables")

    # ✅ Format date like Postman’s "new Date().toUTCString()"
    datetime_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # ✅ Combine path and query (e.g., /endpoint?param=value)
    full_path = path + ("?%s" % query_string if query_string else "")

    # ✅ Build request line and signing payload
    request_line = "%s %s HTTP/1.1" % (method.upper(), full_path)
    payload = "date: %s\n%s" % (datetime_str, request_line)

    # ✅ Generate HMAC-SHA256 signature (same as CryptoJS.HmacSHA256)
    digest = hmac.new(client_secret.encode(), payload.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()

    # ✅ Format the Authorization header exactly as Mekari expects
    authorization_header = (
        'hmac username="%s", algorithm="hmac-sha256", headers="date request-line", signature="%s"' % (client_id, signature)
    )

    # ✅ Return all required headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Date": datetime_str,
        "Authorization": authorization_header,
    }

    return headers




def get_all_contacts(request):
    path = "/qontak/crm/contacts"

    headers = generate_hmac_headers("GET", path)
    url = "https://%s%s" % (os.getenv('MEKARI_URL'), path)

    response = requests.get(url, headers=headers)
    data = response.json() if response.content else {}

    return JsonResponse(data, safe=False)

