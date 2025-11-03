import requests
import json
from django.http import JsonResponse


def get_token_from_refresh():
    """
    Refresh the Qontak access token using requests (based on Qontak’s example).
    """
    url = "https://app.qontak.com/oauth/token"

    client_id = "7081ae8fd19319d15260732c931d8daeb9fdace21adb39186b6c0bfd548b0db7"
    client_secret = "4b27495f82d98f203038fbd8093e38749e8ad4432b68489833b6e6ca9458d87a"
    refresh_token = "e06733bcdeb348709cbbee04594d548914178be17fe36388620bb84ce518fbe1"
    redirect_uri = "https://taratechid.pythonanywhere.com/api/chongqinghotpot/get-all-contacts/"

    # Qontak’s payload format (same as example)
    payload = (
        f"grant_type=refresh_token"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&Content-Type=application%2Fx-www-form-urlencoded"
        f"&client_secret={client_secret}"
        f"&refresh_token={refresh_token}"
    )

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, data=payload)

    print("🟡 TOKEN REFRESH RESPONSE:", response.status_code, response.text)

    try:
        token_data = response.json()
        return token_data.get("access_token")
    except Exception as e:
        print("❌ Error parsing token response:", str(e))
        return None


def get_all_contacts(request):
    """
    Retrieve CRM contacts from Qontak using the refreshed access token.
    """
    token = get_token_from_refresh()
    if not token:
        return JsonResponse({"error": "Failed to get access token"}, status=500)

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

    print("🟢 CONTACTS RESPONSE:", response.status_code, response.text)

    try:
        data = response.json()
    except Exception:
        data = {"raw_text": response.text}

    return JsonResponse(data, safe=False, status=response.status_code)
