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
    request_line = "%s %s HTTP/1.1" % (method.upper(), path)
    signing_string = "date: %s\n%s" % (dt, request_line)

    signature = base64.b64encode(
        hmac.new(
            os.getenv('CQ_HOTPOT_QONTAK_CLIENT_SECRET').encode(),
            signing_string.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    auth_header = (
        'hmac username="%s", algorithm="hmac-sha256", headers="date request-line", signature="%s"' % (os.getenv('CQ_HOTPOT_QONTAK_CLIENT_ID'), signature)
    )

    return {
        "Authorization": "Bearer %s" % os.getenv('CQ_HOTPOT_QONTAK_ACCESS_TOKEN'),
    }


def send_mekari_request(method: str, path: str, payload=None):
    headers = generate_headers(method, path)
    url = "https://%s%s" % (os.getenv('MEKARI_URL'), path)
    resp = requests.request(method.upper(), url, headers=headers, json=payload)
    try:
        return {"http_code": resp.status_code, "body": resp.json()}
    except Exception:
        return {"http_code": resp.status_code, "body": resp.text}

def get_all_contacts(request):
    """
    Retrieve all contacts from a specific Qontak contact list.
    """
    path = "/api/open/v1/contacts/contact_lists"
    result = send_mekari_request("GET", path)

    if result["http_code"] != 200:
        print("Failed to fetch contacts:", result)
        return []

    # data = result["body"].get("data", [])
    # print("Retrieved %s contacts" % len(data))
    # return data
    return result
