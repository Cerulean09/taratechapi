from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import send_facebook_event, send_google_event

@csrf_exempt
def track_event(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        event_name = data.get("event")
        email = data.get("email")
        # phone = data.get("phone")
        # client_id = data.get("client_id", "555.123")  # fallback client ID

        fb_resp = send_facebook_event(event_name, email=email)
        # ga_resp = send_google_event( event_name, {"source": "flutter_app"})

        return JsonResponse({"facebook": fb_resp})
    return JsonResponse({"error": "Only POST allowed"}, status=405)
