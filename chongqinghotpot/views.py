import requests
from django.http import JsonResponse

def get_token():
    """
    Get Qontak OAuth access token using CRM username/password.
    """
    url = "https://app.qontak.com/oauth/token"

    data = {
        "grant_type": "password",
        "client_id": "7081ae8fd19319d15260732c931d8daeb9fdace21adb39186b6c0bfd548b0db7",
        "client_secret": "4b27495f82d98f203038fbd8093e38749e8ad4432b68489833b6e6ca9458d87a",
        "username": "callcenter@chongqinghotpot.id",
        "password": "PassWord88@00",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, data=data)

    print("🟡 Token Response Code:", response.status_code)
    print("🟡 Token Response Body:", response.text)

    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")

    return {
        "error": "Token request failed",
        "status_code": response.status_code,
        "body": response.text,
    }


def get_all_contacts(request):
    """
    Retrieve all CRM contacts from Qontak using Bearer token authentication.
    """
    token_info = get_token()
    print("🟠 Token info:", token_info)

    if isinstance(token_info, dict) and "error" in token_info:
        return JsonResponse(token_info, status=500)

    token = token_info

    url = "https://app.qontak.com/api/v3.1/contacts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    print("🟢 Contacts Response Code:", response.status_code)
    print("🟢 Contacts Response Body:", response.text)

    try:
        data = response.json()
    except Exception:
        data = {"raw_text": response.text}

    return JsonResponse(data, safe=False, status=response.status_code)
