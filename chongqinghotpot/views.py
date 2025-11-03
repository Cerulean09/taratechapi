import json
import http.client
import requests
from django.http import JsonResponse


def get_token():
    """
    Get Qontak OAuth access token using CRM username/password (no client_id needed).
    """
    crm_username = 'callcenter@chongqinghotpot.id'
    password = 'PassWord88@00'

    conn = http.client.HTTPSConnection("app.qontak.com")
    payload = f'grant_type=password&username={crm_username}&password={password}'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
    }

    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")

    try:
        token_data = json.loads(data)
        return token_data.get("access_token")
    except Exception as e:
        print("Error parsing token response:", e)
        print("Raw token response:", data)
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

    # You can include optional query parameters (example: ?page=1&per_page=25)
    params = {
        "page": 1,
        "per_page": 25,
    }

    response = requests.get(url, headers=headers, params=params)

    try:
        data = response.json()
    except Exception:
        data = {"error": response.text}

    print("Response:", data)
    return JsonResponse(data, safe=False, status=response.status_code)
