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
        print("🟡 Token Response Code:", response.status_code)
        print("🟡 Token Response Body:", response.text)

        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")

        # Return full context for debugging
        return {
            "error": "Token request failed",
            "status_code": response.status_code,
            "body": response.text,
        }

    except Exception as e:
        print("❌ Exception in get_token:", str(e))
        return {"error": str(e)}


def get_all_contacts(request):
    """
    Retrieve all CRM contacts from Qontak using Bearer token authentication.
    """
    token_info = get_token()
    print("🟠 Token info:", token_info)

    # If token_info is dict, it means token request failed
    if isinstance(token_info, dict) and "error" in token_info:
        return JsonResponse(token_info, status=500)

    token = token_info

    url = "https://app.qontak.com/api/v3.1/contacts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        print("🟢 Contacts Response Code:", response.status_code)
        print("🟢 Contacts Response Body:", response.text)

        try:
            data = response.json()
        except Exception:
            data = {"raw_text": response.text}

        return JsonResponse(data, safe=False, status=response.status_code)

    except Exception as e:
        print("❌ Exception in get_all_contacts:", str(e))
        return JsonResponse({"error": str(e)}, status=500)
