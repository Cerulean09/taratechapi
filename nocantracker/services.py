# nocantracker/services.py
import os
import requests
import time
import hashlib

# === META PIXEL ===
META_PIXEL_ID = os.getenv("META_PIXEL_ID")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")


def send_facebook_event(event_name, email=None):
    if not META_PIXEL_ID or not META_ACCESS_TOKEN:
        return {
            "status_code": 500,
            "error": "Missing META_PIXEL_ID or META_ACCESS_TOKEN environment variables.",
        }

    url = f"https://graph.facebook.com/v19.0/{META_PIXEL_ID}/events"
    user_data = {}
    if email:
        user_data["em"] = [hashlib.sha256(email.strip().lower().encode()).hexdigest()]

    event = {
        "event_name": event_name,
        "event_time": int(time.time()),
        "action_source": "website",
        "user_data": user_data,
    }

    # Add defaults if no user data
    if not user_data:
        event["custom_data"] = {
            "content_ids": ["default"],
            "content_type": "product",
            "currency": "IDR",
            "value": 0.0,
        }

    if not email:
        return {"status_code": 400,
            "error": "Email is required for this event, current user data: " + str(user_data)}


    payload = {"data": [event]}
    resp = requests.post(url, params={"access_token": META_ACCESS_TOKEN}, json=payload, timeout=10)
    try:
        return resp.json()
    except Exception:
        return {"status_code": resp.status_code, "text": resp.text}



# === GOOGLE ANALYTICS 4 ===
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID")
GA_API_SECRET = os.getenv("GA_API_SECRET")


def send_google_event(client_id, event_name, params=None):
    if not GA_MEASUREMENT_ID or not GA_API_SECRET:
        return {
            "status_code": 500,
            "error": "Missing GA_MEASUREMENT_ID or GA_API_SECRET environment variables.",
        }

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"
    payload = {
        "client_id": client_id,  # e.g., UUID per user/device
        "events": [{
            "name": event_name,
            "params": params or {}
        }]
    }
    response = requests.post(url, json=payload)
    return response.json()
