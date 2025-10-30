from django.http import JsonResponse
import os, hmac, hashlib, base64, requests
from datetime import datetime, timezone

def generate_headers(method: str, path: str):
    dt = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    request_line = f"{method.upper()} {path} HTTP/1.1"
    signing_string = f"date: {dt}\n{request_line}"

    client_secret = os.getenv("CQ_HOTPOT_QONTAK_CLIENT_SECRET")
    client_id = os.getenv("CQ_HOTPOT_QONTAK_CLIENT_ID")

    if not client_secret or not client_id:
        return {"error": "Missing Mekari credentials"}

    signature = base64.b64encode(
        hmac.new(client_secret.encode(), signing_string.encode(), hashlib.sha256).digest()
    ).decode()

    auth_header = (
        f'hmac username="{client_id}", '
        f'algorithm="hmac-sha256", headers="date request-line", signature="{signature}"'
    )

    return {
        "Authorization": auth_header,
        "Date": dt,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def send_mekari_request(method: str, path: str, payload=None):
    headers = generate_headers(method, path)
    if "error" in headers:
        return {"http_code": 500, "body": headers}

    base_url = os.getenv("MEKARI_URL", "api.mekari.com")
    url = f"https://{base_url}{path}"

    try:
        resp = requests.request(method.upper(), url, headers=headers, json=payload)
        data = resp.json() if resp.content else {}
        return {"http_code": resp.status_code, "body": data}
    except Exception as e:
        return {"http_code": 500, "body": {"error": str(e)}}


def get_all_contacts(request):
    """
    Retrieve all contacts from a specific Qontak contact list.
    """
    path = "/qontak/chat/v1/contacts/contact_lists/contacts/534bd3d4-5395-46a9-bfbb-353f3a7721be"
    result = send_mekari_request("GET", path)

    if result["http_code"] != 200:
        print("Failed to fetch contacts:", result)
        return JsonResponse(result, status=result["http_code"], safe=False)

    data = result["body"].get("data", [])
    print(f"Retrieved {len(data)} contacts")

    # ✅ Always return an HTTP response
    return JsonResponse({"contacts": data}, safe=False)
