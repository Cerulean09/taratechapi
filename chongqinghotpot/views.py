import os
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timezone
from django.http import JsonResponse

# ---- CONFIG ----
MEKARI_CLIENT_ID = os.getenv('MEKARI_CLIENT_ID')
MEKARI_CLIENT_SECRET = os.getenv('MEKARI_CLIENT_SECRET')
BASE_URL = "https://api.mekari.com"

def generate_hmac_headers(method: str, path: str):
    """
    Generate headers exactly matching Mekari's HMAC validator requirements.
    """
    # RFC7231 UTC datetime
    date_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Mekari signing string
    request_line = f"{method.upper()} {path} HTTP/1.1"
    signing_string = f"date: {date_str}\n{request_line}"

    # Generate HMAC-SHA256 signature
    signature = base64.b64encode(
        hmac.new(
            MEKARI_CLIENT_SECRET.encode(),
            signing_string.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    authorization = (
        f'hmac username="{MEKARI_CLIENT_ID}", '
        f'algorithm="hmac-sha256", headers="date request-line", '
        f'signature="{signature}"'
    )

    return {
        "Authorization": authorization,
        "Date": date_str,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def get_crm_contacts(request):
    """
    Fetch contacts from Qontak CRM.
    """
    path = "/qontak/crm/contacts"
    url = f"{BASE_URL}{path}"
    headers = generate_hmac_headers("GET", path)

    response = requests.get(url, headers=headers)

    # Debug print (optional)
    print("URL:", url)
    print("Headers:", headers)
    print("Response Code:", response.status_code)
    print("Response Text:", response.text)

    try:
        return JsonResponse(response.json(), safe=False, status=response.status_code)
    except Exception:
        return JsonResponse(
            {"error": "Invalid JSON response", "raw": response.text},
            safe=False,
            status=response.status_code,
        )
