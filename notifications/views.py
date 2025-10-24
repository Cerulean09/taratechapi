from django.shortcuts import render

from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.html import strip_tags
import json
from datetime import datetime

@csrf_exempt
def send_login_notification(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_email = data.get("email")
    username = data.get("username")
    login_time = data.get("login_time") or datetime.utcnow().isoformat()

    if not user_email or not username:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    subject = f"Login Notification for {username}"
    html_content = f"""
        <p>Hello <strong>{username}</strong>,</p>
        <p>You have successfully logged in.</p>
        <ul>
            <li><strong>Time:</strong> {login_time}</li>
        </ul>
        <p>If this wasn’t you, please change your password immediately.</p>
    """
    text_content = strip_tags(html_content)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
