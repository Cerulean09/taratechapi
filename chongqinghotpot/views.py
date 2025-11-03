import json
import requests
from django.http import JsonResponse


def get_token():
    """
    Get Qontak OAuth access token using CRM username/password.
    """
    crm_username = 'callcenter@chongqinghotpot.id'
    password = 'PassWord88@00'

    url = "https://app.qontak.com/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "password",
        "username": crm_username,
        "password": password
    }

    response = requests.post(url, headers=headers, data=data)

    print("🟡 Token response code:", response.status_code)
    print("🟡 Token response body:", response.text)

    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")

    return None


def get_all_contacts(request):
    """
    Retrieve all CRM contacts from Qontak using Bearer token authentication.
    """
    token = get_token()
    if not token:
        return JsonResponse({"error": "Failed to retrieve access token"}, status=500)

    url = "https://app.qontak.com/api/v3.1/contacts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    print("🟢 Contacts response code:", response.status_code)
    print("🟢 Contacts response body:", response.text)

    try:
        data = response.json()
    except Exception:
        data = {"error": response.text}

    return JsonResponse(data, safe=False, status=response.status_code)
