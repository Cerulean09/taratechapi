import requests
import json
from django.http import JsonResponse


def get_token_from_refresh():
    """
    Refresh the Qontak access token using your refresh_token.
    Includes detailed debugging logs.
    """
    url = "https://app.qontak.com/oauth/token"

    client_id = "7081ae8fd19319d15260732c931d8daeb9fdace21adb39186b6c0bfd548b0db7"
    client_secret = "4b27495f82d98f203038fbd8093e38749e8ad4432b68489833b6e6ca9458d87a"
    refresh_token = "e06733bcdeb348709cbbee04594d548914178be17fe36388620bb84ce518fbe1"
    redirect_uri = ""

    # Follow Qontak’s exact form-urlencoded string payload format
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

    print("🔵 [DEBUG] Sending token refresh request...")
    print("🔵 URL:", url)
    print("🔵 Headers:", headers)
    print("🔵 Payload:", payload)

    try:
        response = requests.post(url, headers=headers, data=payload)
    except Exception as e:
        print("❌ [ERROR] Request failed:", str(e))
        return {"error": str(e)}

    print("🟡 [DEBUG] Token Response Code:", response.status_code)
    print("🟡 [DEBUG] Token Raw Body:", response.text)

    try:
        token_data = response.json()
        print("🟢 [DEBUG] Parsed Token JSON:", token_data)
    except Exception as e:
        print("❌ [ERROR] Could not parse token response:", str(e))
        return {"error": f"Invalid JSON response: {response.text}"}

    if response.status_code == 200 and "access_token" in token_data:
        print("✅ [SUCCESS] New access token retrieved successfully.")
        return token_data["access_token"]

    print("⚠️ [WARN] Token not retrieved. Full response below:")
    print(json.dumps(token_data, indent=2))
    return {
        "error": "Token request failed",
        "status_code": response.status_code,
        "body": token_data,
    }


def get_all_contacts(request):
    """
    Retrieve CRM contacts from Qontak using a freshly refreshed access token.
    """
    token_info = get_token_from_refresh()
    print("🟠 [DEBUG] Token Info Returned:", token_info)

    if isinstance(token_info, dict) and "error" in token_info:
        return JsonResponse(token_info, status=500)

    token = token_info

    url = "https://app.qontak.com/api/v3.1/contacts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    params = {"page": 1, "per_page": 25}

    print("🔵 [DEBUG] Fetching contacts...")
    print("🔵 URL:", url)
    print("🔵 Headers:", headers)
    print("🔵 Params:", params)

    try:
        response = requests.get(url, headers=headers, params=params)
    except Exception as e:
        print("❌ [ERROR] Failed to fetch contacts:", str(e))
        return JsonResponse({"error": str(e)}, status=500)

    print("🟢 [DEBUG] Contacts Response Code:", response.status_code)
    print("🟢 [DEBUG] Contacts Raw Body:", response.text)

    try:
        data = response.json()
        print("🟢 [DEBUG] Parsed Contacts JSON:", json.dumps(data, indent=2))
    except Exception as e:
        print("❌ [ERROR] Failed to parse contacts JSON:", str(e))
        data = {"raw_text": response.text}

    return JsonResponse(data, safe=False, status=response.status_code)
