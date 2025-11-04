import hmac
import hashlib
import base64
from datetime import datetime, timezone 
import os
import requests
from django.http import JsonResponse
import hashlib
import base64
from datetime import datetime, timezone

def create_headers(method, path, client_id, client_secret, fixed_date=None):
    """
    Create Mekari-style HMAC authentication headers (100% validator compatible).
    """

    # Mekari requires RFC 1123 date format (same as JS new Date().toUTCString())
    dt = fixed_date or datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # --- Construct the canonical request-line exactly ---
    # e.g. GET /qontak/crm/contacts/info HTTP/1.1
    request_line = method.upper() + " " + path + " HTTP/1.1"

    # --- Signing string ---
    # Must match Mekari's: "date: <date>\n<request_line>"
    signing_string = "date: " + dt + "\n" + request_line

    # --- Generate HMAC SHA256 signature ---
    signature_bytes = hmac.new(
        client_secret.encode("utf-8"),
        signing_string.encode("utf-8"),
        hashlib.sha256
    ).digest()

    signature = base64.b64encode(signature_bytes).decode("utf-8")

    # --- Authorization Header ---
    authorization_header = (
        'hmac username="' + client_id + '", '
        'algorithm="hmac-sha256", '
        'headers="date request-line", '
        'signature="' + signature + '"'
    )

    # --- Return headers ---
    return {
        "Authorization": authorization_header,
        "Date": dt,
        "Content-Type": "application/json"
    }

def get_all_contacts(request):
    """
    Get all CRM contacts from Mekari (Qontak CRM)
    """
    try:
        client_id = os.getenv("CQ_HOTPOT_QONTAK_CLIENT_ID")
        client_secret = os.getenv("CQ_HOTPOT_QONTAK_CLIENT_SECRET")

        path = "/qontak/crm/contacts/info"  # <-- from your example
        headers = create_headers("GET", path, client_id, client_secret)

        url = f"https://api.mekari.com{path}"
        response = requests.get(url, headers=headers)

        # Debugging info (optional)
        print("Request URL:", url)
        print("Headers:", headers)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)

        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
