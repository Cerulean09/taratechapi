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

    try:
        response = requests.post(url, headers=headers, data=data)
        print("Token Response Code:", response.status_code)
        print("Token Response Body:", response.text)

        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")

        return None
    except Exception as e:
        print("Error requesting token:", str(e))
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

    params = {
        "page": 1,
        "per_page": 25,
    }

    response = requests.get(url, headers=headers, params=params)

    try:
        data = response.json()
    except Exception:
        data = {"error": response.text}

    print("Contacts Response Code:", response.status_code)
    print("Contacts Response Body:", data)

    return JsonResponse(data, safe=False, status=response.status_code)
