from django.shortcuts import render

from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.html import strip_tags
import json
from datetime import datetime
import requests
import os

from django.conf import settings
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timezone

def generate_headers(method: str, path: str):
    dt = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    request_line = f"{method.upper()} {path} HTTP/1.1"
    signing_string = f"date: {dt}\n{request_line}"

    signature = base64.b64encode(
        hmac.new(
            os.getenv('CQ_HOTPOT_QONTAK_CLIENT_SECRET').encode(),
            signing_string.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    auth_header = (
        f'hmac username="{os.getenv('CQ_HOTPOT_QONTAK_CLIENT_ID')}", '
        f'algorithm="hmac-sha256", '
        f'headers="date request-line", '
        f'signature="{signature}"'
    )

    return {
        "Authorization": auth_header,
        "Date": dt,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def send_mekari_request(method: str, path: str, payload=None):
    headers = generate_headers(method, path)
    url = f"https://{os.getenv('MEKARI_URL')}{path}"
    resp = requests.request(method.upper(), url, headers=headers, json=payload)
    try:
        return {"http_code": resp.status_code, "body": resp.json()}
    except Exception:
        return {"http_code": resp.status_code, "body": resp.text}

def get_all_contacts(request):
    """
    Retrieve all contacts from a specific Qontak contact list.
    """
    path = f"/qontak/chat/v1/contacts/contact_lists/contacts/534bd3d4-5395-46a9-bfbb-353f3a7721be"
    result = send_mekari_request("GET", path)

    if result["http_code"] != 200:
        print("Failed to fetch contacts:", result)
        return []

    data = result["body"].get("data", [])
    print(f"Retrieved {len(data)} contacts")
    return data
