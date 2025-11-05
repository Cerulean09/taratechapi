import hmac
import hashlib
import base64
import requests
import json
from datetime import datetime, timezone
import time
import os
from django.http import JsonResponse
# --------------------------
# CONFIG
# --------------------------
CLIENT_ID = os.getenv('CQ_HOTPOT_QONTAK_CLIENT_ID')
CLIENT_SECRET = os.getenv('CQ_HOTPOT_QONTAK_CLIENT_SECRET')
BASE_URL = "https://api.mekari.com"


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
def send_mekari_request(method: str, path: str, payload: dict = None):
    """
    Send a signed request to Mekari API (GET or POST).
    Equivalent to the PHP send_mekari_request() function.
    """
    url = BASE_URL + path
    headers = generate_headers(method, path, CLIENT_ID, CLIENT_SECRET)

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
# EXAMPLE USAGE
# --------------------------
def example_usage():
    # Example 1: WhatsApp Broadcast (POST)
    post_path = "/qontak/chat/v1/broadcasts/whatsapp/direct"
    post_payload = {
        "to_number": "62xxxxx",  # Replace with real number
        "to_name": "Muhamad Iqbal",
        "message_template_id": "fbd4da17-a20e-4248-993d-f95566ee10b2",
        "channel_integration_id": "a2e9673a-44ac-493d-aac0-51c5a0bfb1a5",
        "language": {"code": "id"},
        "parameters": {
            "body": [
                {"key": "1", "value": "customer_name", "value_text": "Iqbal"},
                {"key": "2", "value": "link_pdf", "value_text": "https://cdn.qontak.com/example.pdf"}
            ]
        }
    }

    print("==[ Sending Broadcast (POST) ]==")
    post_result = send_mekari_request("POST", post_path, post_payload)
    print("Status Code:", post_result["http_code"])
    print(json.dumps(post_result["response"], indent=2))

    if post_result["http_code"] != 201:
        print("❌ Failed to send broadcast.")
        return

    # Extract broadcast_id
    broadcast_id = post_result["response"].get("data", {}).get("id")
    if not broadcast_id:
        print("❌ Broadcast ID not found.")
        return

    # Delay before log check
    print("\nWaiting 10 seconds before checking log...\n")
    time.sleep(10)

    # Example 2: Get Broadcast Log (GET)
    log_path = f"/qontak/chat/v1/broadcasts/{broadcast_id}/whatsapp/log"
    print("==[ Getting Broadcast Log (GET) ]==")
    log_result = send_mekari_request("GET", log_path)
    print("Status Code:", log_result["http_code"])
    print(json.dumps(log_result["response"], indent=2))


def get_all_contacts(request):
    result = send_mekari_request(
    "GET",
    "/qontak/chat/v1/contacts/contact_lists"
    )
    print(result)
    return JsonResponse(result, safe=False, status=result["http_code"])


