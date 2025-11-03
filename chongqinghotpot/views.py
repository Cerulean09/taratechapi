import os, hmac, hashlib, base64, requests
from datetime import datetime, timezone
from django.http import JsonResponse
import http.client

def get_token():
    appId = '7081ae8fd19319d15260732c931d8daeb9fdace21adb39186b6c0bfd548b0db7'
    appSecret = '4b27495f82d98f203038fbd8093e38749e8ad4432b68489833b6e6ca9458d87a'
    crmUsername = 'callcenter@chongqinghotpot.id'
    password = 'PassWord88@00'
    conn = http.client.HTTPSConnection("app.qontak.com")
    payload = 'grant_type=password&Content-Type=application%2Fx-www-form-urlencoded&username={crmUsername}&password={password}'
    headers = {}
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")

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
    token = get_token()
    print(token)
    return JsonResponse(token, safe=False, status=200)
