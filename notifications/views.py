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


@csrf_exempt
def send_signup_notification(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_email = data.get("email")
    username = data.get("username")
    signup_time = data.get("signupTime") or datetime.utcnow().isoformat()

    if not user_email or not username:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    subject = f"Signup Notification for {username}"
    html_content = f"""
        <p>Hello <strong>{username}</strong>,</p>
        <p>You have successfully signed up. Welcome to Tara Tech!</p>
        <ul>
            <li><strong>Time:</strong> {signup_time}</li>
        </ul>
        <p>Thank you for signing up with Tara Tech!</p>
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

@csrf_exempt
def send_reservation_request_notification(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_email = data.get("email")
    username = data.get("username")
    reservation_request_time = data.get("reservationRequestTime") or datetime.utcnow().isoformat() or "N/A"
    outlet_name = data.get("outletName") or "N/A"
    special_request = data.get("specialRequest") or "N/A"
    number_of_guests = data.get("numberOfGuests") or "N/A"

    if not user_email or not username:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    subject = f"Reservation Request Notification for {username}"
    html_content = f"""
        <p>Hello <strong>{username}</strong>,</p>
        <p>You have successfully requested a reservation. Please wait for confirmation!</p>
        <ul>
            <li><strong>Time:</strong> {reservation_request_time}</li>
            <li><strong>Outlet Name:</strong> {outlet_name}</li>
            <li><strong>Number of Guests:</strong> {number_of_guests}</li>
            <li><strong>Special Request:</strong> {special_request}</li>
        </ul>
        <p>Thank you for requesting a reservation with Tara Tech. We will get back to you soon.</p>
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

@csrf_exempt
def send_reservation_confirmation_notification(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_email = data.get("email")
    username = data.get("username")
    reservation_confirmation_time = data.get("reservationConfirmationTime") or datetime.utcnow().isoformat() or "N/A"
    outlet_name = data.get("outletName") or "N/A"
    special_request = data.get("specialRequest") or "N/A"
    number_of_guests = data.get("numberOfGuests") or "N/A"

    if not user_email or not username:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    subject = f"Reservation Confirmation Notification for {username}"
    html_content = f"""
        <p>Hello <strong>{username}</strong>,</p>
        <p>Your reservation has been confirmed. See you there!</p>
        <ul>
            <li><strong>Time:</strong> {reservation_confirmation_time}</li>
            <li><strong>Outlet Name:</strong> {outlet_name}</li>
            <li><strong>Number of Guests:</strong> {number_of_guests}</li>
            <li><strong>Special Request:</strong> {special_request}</li>
        </ul>
        <p>Thank you for using Tara Tech. We can't wait to serve you soon at {outlet_name}.</p>
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


@csrf_exempt
def send_reservation_cancellation_notification(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_email = data.get("email")
    username = data.get("username")
    reservation_cancellation_time = data.get("reservationCancellationTime") or datetime.utcnow().isoformat() or "N/A"
    outlet_name = data.get("outletName") or "N/A"
    special_request = data.get("specialRequest") or "N/A"

    if not user_email or not username:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    subject = f"Reservation Cancellation Notification for {username}"
    html_content = f"""
        <p>Hello <strong>{username}</strong>,</p>
        <p>Your reservation has been cancelled. Reservation Details:</p>
        <ul>
            <li><strong>Time:</strong> {reservation_cancellation_time}</li>
            <li><strong>Outlet Name:</strong> {outlet_name}</li>
            <li><strong>Special Request:</strong> {special_request}</li>
        </ul>
        <p>Thank you for using Tara Tech. We hope to see you again soon.</p>
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