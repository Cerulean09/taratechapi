import hmac
import hashlib
import base64
from datetime import datetime, timezone 
import os
import requests
from django.http import JsonResponse

def create_headers(method: str, full_path: str, client_id: str, client_secret: str):
    """
    Replicates Mekari's Postman HMAC header generator.
    
    Args:
        method (str): HTTP method (GET, POST, PUT, etc.)
        full_path (str): API path including query params (e.g. "/qontak/crm/contacts?page=1")
        client_id (str): Mekari client ID
        client_secret (str): Mekari client secret
    
    Returns:
        dict: Headers including Authorization, Date, and Content-Type
    """
    # 1️⃣ Current GMT date in RFC1123 format (same as new Date().toUTCString())
    dt = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # 2️⃣ Build the request-line string: "GET /path?query HTTP/1.1"
    request_line = f"{method.upper()} {full_path} HTTP/1.1"

    # 3️⃣ Create payload like: "date: Mon, 03 Nov 2025 15:00:00 GMT\nGET /... HTTP/1.1"
    payload = f"date: {dt}\n{request_line}"

    # 4️⃣ Generate HMAC-SHA256 signature (base64 encoded)
    signature_bytes = hmac.new(
        client_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_bytes).decode()

    # 5️⃣ Construct Authorization header (identical to Mekari example)
    authorization_header = (
        f'hmac username="{client_id}", '
        f'algorithm="hmac-sha256", '
        f'headers="date request-line", '
        f'signature="{signature}"'
    )

    # 6️⃣ Return final headers
    return {
        "Content-Type": "application/json",
        "Date": dt,
        "Authorization": authorization_header,
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
