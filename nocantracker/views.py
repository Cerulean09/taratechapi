from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import send_facebook_event

@csrf_exempt
def track_event(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    event_name = data.get("event")
    email = data.get("email")

    if not event_name:
        return JsonResponse({"error": "Missing 'event'"}, status=400)
    if not email or email.strip() == "":
        return JsonResponse({"error": "Email is required for this event"}, status=400)

    fb_resp = send_facebook_event(event_name, email=email, request=request)

    return JsonResponse({"facebook": fb_resp})
