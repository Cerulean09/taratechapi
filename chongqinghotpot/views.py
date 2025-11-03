import os
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timezone
from django.http import JsonResponse

# === CONFIG ===
CLIENT_ID = os.getenv('MEKARI_CLIENT_ID')
CLIENT_SECRET = os.getenv('MEKARI_CLIENT_SECRET')
BASE_URL = "https://api.mekari.com"


def generate_hmac_headers(method, path):
    """
    Generate HMAC headers for Mekari CRM API.
    """
    dt = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Mekari HMAC string
    request_line = f"{method.upper()} {path} HTTP/1.1"
    signing_string = f"date: {dt}\n{request_line}"

    signature = base64.b64encode(
        hmac.new(
            CLIENT_SECRET.encode(),
            signing_string.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    authorization = (
        f'hmac username="{CLIENT_ID}", '
        f'algorithm="hmac-sha256", '
        f'headers="date request-line", '
        f'signature="{signature}"'
    )

    return {
        "Authorization": authorization,
        "Date": dt,
        "Content-Type": "application/json"
    }


def get_crm_contacts(request):
    """
    Sync Qontak CRM contacts into your app.
    """
    path = "/qontak/crm/contacts"
    url = f"{BASE_URL}{path}"

    headers = generate_hmac_headers("GET", path)
    response = requests.get(url, headers=headers)

    try:
        data = response.json()
    except Exception:
        data = {"error": response.text}

    return JsonResponse(data, safe=False, status=response.status_code)
