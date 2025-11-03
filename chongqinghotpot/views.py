import os, hmac, hashlib, base64, requests
from datetime import datetime, timezone
from django.http import JsonResponse

def generate_headers(method, path):
    dt = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    signing_string = f"date: {dt}\n{method.upper()} {path} HTTP/1.1"
    signature = base64.b64encode(
        hmac.new(
            os.getenv('CQ_HOTPOT_QONTAK_CLIENT_SECRET').encode(),
            signing_string.encode(),
            hashlib.sha256
        ).digest()
    ).decode()
    return {
        "Authorization": f'hmac username="{os.getenv("CQ_HOTPOT_QONTAK_CLIENT_ID")}", '
                         f'algorithm="hmac-sha256", headers="date request-line", '
                         f'signature="{signature}"',
        "Date": dt,
        "Content-Type": "application/json",
    }

def get_all_contacts(request):
    path = "/qontak/crm/contacts"
    headers = generate_headers("GET", path)
    url = f"https://api.mekari.com{path}"

    response = requests.get(url, headers=headers)
    return JsonResponse(response.json(), safe=False, status=response.status_code)
