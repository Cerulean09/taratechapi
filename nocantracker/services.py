# nocantracker/services.py
import requests
import time
import hashlib

# === META PIXEL ===
META_PIXEL_ID = "1054777313198157"
META_ACCESS_TOKEN = "EAAUd5UHmwLcBPopDnEjgihWTs4P6Q18V6bQI3IjTCZClDTJl6aZCqoZBGOZBWPIsSbKHrKHkZBZBgZCCv1tEeEuufq5ah3KOXJZB6a9Jn0OWrsZCRLqiga8DQZBStC7ZBqGXcbOaaizPMlZCQLuoB6iDlLnRw82CptH2SsIzUgZCRCqCC3uuxNSPZAM0uJumAiZBUPfzFVSTwZDZD"  # generate in FB Business Manager

def send_facebook_event(event_name, email=None):
    url = f"https://graph.facebook.com/v19.0/{META_PIXEL_ID}/events"
    user_data = {}
    if email:
        user_data["em"] = [hashlib.sha256(email.strip().lower().encode()).hexdigest()]
    # if phone:
    #     user_data["ph"] = [hashlib.sha256(phone.strip().encode()).hexdigest()]

    payload = {
        "data": [{
            "event_name": event_name,
            "event_time": int(time.time()),
            "action_source": "website",
            "user_data": user_data,
        }]
    }
    response = requests.post(url, params={"access_token": META_ACCESS_TOKEN}, json=payload)
    return response.json()


# === GOOGLE ANALYTICS 4 ===
GA_MEASUREMENT_ID = "G-XXXXXXXX"   # fill from docx / GA4 setup
GA_API_SECRET = "<YOUR_API_SECRET>"

def send_google_event(client_id, event_name, params=None):
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
