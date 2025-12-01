from django.shortcuts import render

from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.conf import settings
import json
from datetime import datetime, timedelta
import random

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
            <li><strong>Time:</strong> {login_time.replace('T',' ').replace('Z','')}</li>
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
            <li><strong>Time:</strong> {signup_time.replace('T',' ').replace('Z','')}</li>
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
            <li><strong>Date and Time:</strong> {reservation_request_time.replace('T',' ').replace('Z','')}</li>
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
            <li><strong>Date and Time:</strong> {reservation_confirmation_time.replace('T',' ').replace('Z','')}</li>
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
            <li><strong>Time:</strong> {reservation_cancellation_time.replace('T',' ').replace('Z','')}</li>
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

@csrf_exempt
def send_payment_pending_notification(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_email = data.get("email")
    username = data.get("username")
    payment_url = data.get("paymentUrl")
    amount = data.get("amount") or "N/A"
    reservation_id = data.get("reservationId") or "N/A"
    outlet_name = data.get("outletName") or "N/A"
    payment_time = data.get("paymentTime") or datetime.utcnow().isoformat()

    if not user_email or not username:
        return JsonResponse({"error": "Missing required fields: email and username"}, status=400)
    
    if not payment_url:
        return JsonResponse({"error": "Missing required field: paymentUrl"}, status=400)

    subject = f"Payment Pending Notification for {username}"
    
    # HTML content with styled Pay Now button
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #007bff;
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
                text-align: center;
            }}
            .button:hover {{
                background-color: #0056b3;
            }}
            .info-box {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .info-box ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            .info-box li {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <p>Hello <strong>{username}</strong>,</p>
            <p>You have a pending payment for your reservation. Please complete the payment to confirm your reservation.</p>
            
            <div class="info-box">
                <ul>
                    <li><strong>Reservation ID:</strong> {reservation_id}</li>
                    <li><strong>Amount:</strong> {amount}</li>
                    <li><strong>Outlet Name:</strong> {outlet_name}</li>
                    <li><strong>Payment Request Time:</strong> {payment_time.replace('T',' ').replace('Z','')}</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{payment_url}" class="button">Pay Now</a>
            </div>
            
            <p>If the button above doesn't work, please copy and paste the following link into your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{payment_url}</p>
            
            <p><strong>Note:</strong> This payment link will expire soon. Please complete your payment as soon as possible to secure your reservation.</p>
            
            <p>Thank you for using Tara Tech!</p>
        </div>
    </body>
    </html>
    """
    
    # Plain text version for email clients that don't support HTML
    text_content = f"""
Hello {username},

You have a pending payment for your reservation. Please complete the payment to confirm your reservation.

Reservation Details:
- Reservation ID: {reservation_id}
- Amount: {amount}
- Outlet Name: {outlet_name}
- Payment Request Time: {payment_time.replace('T',' ').replace('Z','')}

Please click the following link to complete your payment:
{payment_url}

Note: This payment link will expire soon. Please complete your payment as soon as possible to secure your reservation.

Thank you for using Tara Tech!
    """

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
def send_forgot_password_otp_notification(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_email = data.get("email")
    username = data.get("username") or "User"

    if not user_email:
        return JsonResponse({"error": "Missing required field: email"}, status=400)

    # Generate 6-digit OTP code
    otp_code = str(random.randint(100000, 999999))
    
    # Generate expiration timestamp (15 minutes from now)
    current_time = datetime.utcnow()
    expiration_time = current_time + timedelta(minutes=15)
    expiration_timestamp = expiration_time.timestamp()
    expiration_iso = expiration_time.isoformat()

    subject = f"Forgot Password OTP Notification for {username}"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .otp-box {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
            }}
            .otp-code {{
                font-size: 32px;
                font-weight: bold;
                color: #007bff;
                letter-spacing: 5px;
                margin: 10px 0;
            }}
            .warning-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <p>Hello <strong>{username}</strong>,</p>
            <p>You have requested to reset your password. Please use the OTP code below to proceed:</p>
            
            <div class="otp-box">
                <p style="margin: 0; font-size: 14px; color: #666;">Your OTP Code:</p>
                <div class="otp-code">{otp_code}</div>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">This code will expire in 15 minutes</p>
            </div>
            
            <div class="warning-box">
                <p style="margin: 0;"><strong>⚠️ Security Notice:</strong></p>
                <p style="margin: 5px 0 0 0;">Never share this OTP code with anyone. If you didn't request this password reset, please ignore this email.</p>
            </div>
            
            <p><strong>The OTP will expire in 10 minutes</strong> </p>
            
            <p>Thank you for using Tara Tech!</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
Hello {username},

You have requested to reset your password. Please use the OTP code below to proceed:

Your OTP Code: {otp_code}

This code will expire in 15 minutes.

Expiration Time: {expiration_iso.replace('T',' ').replace('Z','')} UTC

⚠️ Security Notice: Never share this OTP code with anyone. If you didn't request this password reset, please ignore this email.

Thank you for using Tara Tech!
    """

    try:
        # Use DEFAULT_FROM_EMAIL if set, otherwise fall back to EMAIL_HOST_USER
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return JsonResponse({
            "status": "success",
            "otp": otp_code,
            "expiresAt": expiration_timestamp,
            "expiresAtIso": expiration_iso,
            "email": user_email
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def ecosuite_on_hold_notification(request):
    """
    Send notification when an Ecosuite reservation is placed on hold.
    Informs the customer that their booking is received and they will receive 
    a confirmation message 2 days prior to their booking.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Required fields
    user_email = data.get("email")
    customer_name = data.get("customerName")
    
    # Optional fields with defaults
    reservation_id = data.get("reservationId") or "N/A"
    reservation_date_time = data.get("reservationDateTime") or "N/A"
    number_of_guests = data.get("numberOfGuests") or "N/A"
    outlet_name = data.get("outletName") or "Our Restaurant"
    brand_name = data.get("brandName") or "Tara Tech"
    notes = data.get("notes") or None
    confirmation_link = data.get("confirmationLink") or None

    if not user_email or not customer_name:
        return JsonResponse({"error": "Missing required fields: email and customerName"}, status=400)

    # Format the date/time if it's in ISO format
    formatted_date_time = reservation_date_time
    try:
        if 'T' in reservation_date_time:
            dt = datetime.fromisoformat(reservation_date_time.replace('Z', '+00:00'))
            formatted_date_time = dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        formatted_date_time = reservation_date_time.replace('T', ' ').replace('Z', '')

    subject = f"Booking Received - {brand_name} Reservation"
    
    # HTML content with modern styling
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
            }}
            .header {{
                text-align: center;
                padding: 30px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px 10px 0 0;
            }}
            .header-icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .status-badge {{
                display: inline-block;
                background-color: #ffc107;
                color: #856404;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 14px;
                margin: 20px 0;
            }}
            .info-box {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }}
            .info-box h3 {{
                margin: 0 0 15px 0;
                color: #667eea;
                font-size: 18px;
            }}
            .info-row {{
                display: flex;
                padding: 8px 0;
                border-bottom: 1px solid #e9ecef;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                flex: 0 0 140px;
                font-weight: 600;
                color: #666;
            }}
            .info-value {{
                flex: 1;
                color: #333;
            }}
            .reminder-box {{
                background-color: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .reminder-box .icon {{
                font-size: 24px;
                margin-bottom: 10px;
            }}
            .button {{
                display: inline-block;
                padding: 14px 32px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                margin: 20px 0;
                text-align: center;
            }}
            .button:hover {{
                opacity: 0.9;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
                border-top: 1px solid #e9ecef;
                margin-top: 30px;
            }}
            @media only screen and (max-width: 600px) {{
                .info-row {{
                    flex-direction: column;
                }}
                .info-label {{
                    margin-bottom: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-icon">🎉</div>
                <h1>Booking Received!</h1>
            </div>
            
            <div class="content">
                <p>Hello <strong>{customer_name}</strong>,</p>
                <p>Great news! Your reservation request has been received and is currently <strong>on hold</strong> for you.</p>
                
                <div style="text-align: center;">
                    <span class="status-badge">⏳ ON HOLD</span>
                </div>
                
                <div class="info-box">
                    <h3>Reservation Details</h3>
                    <div class="info-row">
                        <div class="info-label">Reservation ID:</div>
                        <div class="info-value">{reservation_id}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Date & Time:</div>
                        <div class="info-value">{formatted_date_time}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Number of Guests:</div>
                        <div class="info-value">{number_of_guests}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Location:</div>
                        <div class="info-value">{outlet_name}</div>
                    </div>
                    {f'''<div class="info-row">
                        <div class="info-label">Notes:</div>
                        <div class="info-value">{notes}</div>
                    </div>''' if notes else ''}
                </div>
                
                <div class="reminder-box">
                    <div class="icon">📅</div>
                    <p style="margin: 0; font-weight: 600; color: #0d47a1;">Confirmation Reminder</p>
                    <p style="margin: 10px 0 0 0; color: #1565c0;">
                        You will receive a confirmation message <strong>2 days before your booking</strong> to ensure everything is ready for your visit.
                    </p>
                </div>
                
                {f'''<div style="text-align: center; margin: 30px 0;">
                    <a href="{confirmation_link}" class="button">View My Reservation</a>
                </div>
                
                <p style="text-align: center; font-size: 14px; color: #666;">
                    Or copy this link: <span style="color: #667eea; word-break: break-all;">{confirmation_link}</span>
                </p>''' if confirmation_link else ''}
                
                <p style="margin-top: 30px;">If you have any questions or need to make changes to your reservation, please don't hesitate to contact us.</p>
                
                <p style="margin-top: 20px;">We look forward to serving you at <strong>{outlet_name}</strong>!</p>
                
                <p style="margin-top: 20px;">Best regards,<br>
                <strong>{brand_name} Team</strong></p>
            </div>
            
            <div class="footer">
                <p style="margin: 5px 0;">© {datetime.now().year} {brand_name}. All rights reserved.</p>
                <p style="margin: 5px 0; font-size: 12px;">This is an automated notification. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
Hello {customer_name},

Great news! Your reservation request has been received and is currently ON HOLD for you.

RESERVATION DETAILS:
- Reservation ID: {reservation_id}
- Date & Time: {formatted_date_time}
- Number of Guests: {number_of_guests}
- Location: {outlet_name}
{f'- Notes: {notes}' if notes else ''}

📅 CONFIRMATION REMINDER:
You will receive a confirmation message 2 days before your booking to ensure everything is ready for your visit.

{f'View your reservation: {confirmation_link}' if confirmation_link else ''}

If you have any questions or need to make changes to your reservation, please don't hesitate to contact us.

We look forward to serving you at {outlet_name}!

Best regards,
{brand_name} Team

---
© {datetime.now().year} {brand_name}. All rights reserved.
This is an automated notification. Please do not reply to this email.
    """

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return JsonResponse({"status": "success", "email": user_email})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def ecosuite_confirmed_status(request):
    """
    Send notification when an Ecosuite reservation is confirmed.
    Informs the customer that their reservation has been confirmed with all details.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Required fields
    user_email = data.get("email")
    customer_name = data.get("customerName")
    
    # Optional fields with defaults
    reservation_id = data.get("reservationId") or "N/A"
    reservation_date_time = data.get("reservationDateTime") or "N/A"
    number_of_guests = data.get("numberOfGuests") or "N/A"
    outlet_name = data.get("outletName") or "Our Restaurant"
    brand_name = data.get("brandName") or "Tara Tech"
    outlet_address = data.get("outletAddress") or None
    notes = data.get("notes") or None
    table_number = data.get("tableNumber") or None

    if not user_email or not customer_name:
        return JsonResponse({"error": "Missing required fields: email and customerName"}, status=400)

    # Format the date/time if it's in ISO format
    formatted_date_time = reservation_date_time
    try:
        if 'T' in reservation_date_time:
            dt = datetime.fromisoformat(reservation_date_time.replace('Z', '+00:00'))
            formatted_date_time = dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        formatted_date_time = reservation_date_time.replace('T', ' ').replace('Z', '')

    subject = f"Reservation Confirmed - {brand_name}"
    
    # HTML content with modern styling
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
            }}
            .header {{
                text-align: center;
                padding: 30px 20px;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                border-radius: 10px 10px 0 0;
            }}
            .header-icon {{
                font-size: 64px;
                margin-bottom: 10px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 32px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .status-badge {{
                display: inline-block;
                background-color: #d4edda;
                color: #155724;
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 16px;
                margin: 20px 0;
            }}
            .info-box {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #10b981;
            }}
            .info-box h3 {{
                margin: 0 0 15px 0;
                color: #10b981;
                font-size: 18px;
            }}
            .info-row {{
                display: flex;
                padding: 10px 0;
                border-bottom: 1px solid #e9ecef;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                flex: 0 0 140px;
                font-weight: 600;
                color: #666;
            }}
            .info-value {{
                flex: 1;
                color: #333;
                font-weight: 500;
            }}
            .highlight-box {{
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border-left: 4px solid #10b981;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .highlight-box .icon {{
                font-size: 32px;
                margin-bottom: 10px;
            }}
            .important-info {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
                border-top: 1px solid #e9ecef;
                margin-top: 30px;
            }}
            @media only screen and (max-width: 600px) {{
                .info-row {{
                    flex-direction: column;
                }}
                .info-label {{
                    margin-bottom: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-icon">✅</div>
                <h1>Reservation Confirmed!</h1>
            </div>
            
            <div class="content">
                <p>Hello <strong>{customer_name}</strong>,</p>
                <p>Wonderful news! Your reservation has been <strong>confirmed</strong> and we're excited to welcome you!</p>
                
                <div style="text-align: center;">
                    <span class="status-badge">✓ CONFIRMED</span>
                </div>
                
                <div class="info-box">
                    <h3>Reservation Details</h3>
                    <div class="info-row">
                        <div class="info-label">Reservation ID:</div>
                        <div class="info-value">{reservation_id}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Date & Time:</div>
                        <div class="info-value">{formatted_date_time}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Number of Guests:</div>
                        <div class="info-value">{number_of_guests}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Location:</div>
                        <div class="info-value">{outlet_name}</div>
                    </div>
                    {f'''<div class="info-row">
                        <div class="info-label">Table Number:</div>
                        <div class="info-value">{table_number}</div>
                    </div>''' if table_number else ''}
                    {f'''<div class="info-row">
                        <div class="info-label">Address:</div>
                        <div class="info-value">{outlet_address}</div>
                    </div>''' if outlet_address else ''}
                    {f'''<div class="info-row">
                        <div class="info-label">Special Requests:</div>
                        <div class="info-value">{notes}</div>
                    </div>''' if notes else ''}
                </div>
                
                <div class="highlight-box">
                    <div class="icon">🎉</div>
                    <p style="margin: 0; font-weight: 600; color: #065f46; font-size: 18px;">We're Ready for You!</p>
                    <p style="margin: 10px 0 0 0; color: #047857;">
                        Your table is reserved and waiting. We've prepared everything to make your visit memorable!
                    </p>
                </div>
                
                <div class="important-info">
                    <p style="margin: 0; font-weight: 600;">⏰ Please Note:</p>
                    <p style="margin: 5px 0 0 0;">Please arrive on time. If you need to make any changes or cancel, please contact us as soon as possible.</p>
                </div>
                
                <p style="margin-top: 30px;">If you have any questions or special requests, please don't hesitate to contact us.</p>
                
                <p style="margin-top: 20px;">We look forward to serving you at <strong>{outlet_name}</strong>!</p>
                
                <p style="margin-top: 20px;">Best regards,<br>
                <strong>{brand_name} Team</strong></p>
            </div>
            
            <div class="footer">
                <p style="margin: 5px 0;">© {datetime.now().year} {brand_name}. All rights reserved.</p>
                <p style="margin: 5px 0; font-size: 12px;">This is an automated notification. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
Hello {customer_name},

Wonderful news! Your reservation has been CONFIRMED and we're excited to welcome you!

✓ RESERVATION CONFIRMED

RESERVATION DETAILS:
- Reservation ID: {reservation_id}
- Date & Time: {formatted_date_time}
- Number of Guests: {number_of_guests}
- Location: {outlet_name}
{f'- Table Number: {table_number}' if table_number else ''}
{f'- Address: {outlet_address}' if outlet_address else ''}
{f'- Special Requests: {notes}' if notes else ''}

🎉 WE'RE READY FOR YOU!
Your table is reserved and waiting. We've prepared everything to make your visit memorable!

⏰ PLEASE NOTE:
Please arrive on time. If you need to make any changes or cancel, please contact us as soon as possible.

If you have any questions or special requests, please don't hesitate to contact us.

We look forward to serving you at {outlet_name}!

Best regards,
{brand_name} Team

---
© {datetime.now().year} {brand_name}. All rights reserved.
This is an automated notification. Please do not reply to this email.
    """

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return JsonResponse({"status": "success", "email": user_email})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def ecosuite_cancelled_notification(request):
    """
    Send notification when an Ecosuite reservation is cancelled.
    Informs the customer that their reservation has been cancelled.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Required fields
    user_email = data.get("email")
    customer_name = data.get("customerName")
    
    # Optional fields with defaults
    reservation_id = data.get("reservationId") or "N/A"
    reservation_date_time = data.get("reservationDateTime") or "N/A"
    number_of_guests = data.get("numberOfGuests") or "N/A"
    outlet_name = data.get("outletName") or "Our Restaurant"
    brand_name = data.get("brandName") or "Tara Tech"
    cancellation_reason = data.get("cancellationReason") or None
    cancelled_by = data.get("cancelledBy") or "customer"  # "customer" or "restaurant"
    new_booking_link = data.get("newBookingLink") or None

    if not user_email or not customer_name:
        return JsonResponse({"error": "Missing required fields: email and customerName"}, status=400)

    # Format the date/time if it's in ISO format
    formatted_date_time = reservation_date_time
    try:
        if 'T' in reservation_date_time:
            dt = datetime.fromisoformat(reservation_date_time.replace('Z', '+00:00'))
            formatted_date_time = dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        formatted_date_time = reservation_date_time.replace('T', ' ').replace('Z', '')

    subject = f"Reservation Cancelled - {brand_name}"
    
    # Customize message based on who cancelled
    if cancelled_by.lower() == "customer":
        main_message = "Your reservation has been <strong>cancelled</strong> as requested."
        closing_message = "We hope to see you again soon! Feel free to make a new reservation anytime."
    else:
        main_message = "Unfortunately, your reservation has been <strong>cancelled</strong>."
        closing_message = "We sincerely apologize for any inconvenience. We hope you'll give us another opportunity to serve you."
    
    # HTML content with modern styling
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
            }}
            .header {{
                text-align: center;
                padding: 30px 20px;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border-radius: 10px 10px 0 0;
            }}
            .header-icon {{
                font-size: 64px;
                margin-bottom: 10px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 32px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .status-badge {{
                display: inline-block;
                background-color: #f8d7da;
                color: #721c24;
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 16px;
                margin: 20px 0;
            }}
            .info-box {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #dc3545;
            }}
            .info-box h3 {{
                margin: 0 0 15px 0;
                color: #dc3545;
                font-size: 18px;
            }}
            .info-row {{
                display: flex;
                padding: 10px 0;
                border-bottom: 1px solid #e9ecef;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                flex: 0 0 140px;
                font-weight: 600;
                color: #666;
            }}
            .info-value {{
                flex: 1;
                color: #333;
            }}
            .action-box {{
                background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
                border-left: 4px solid #0ea5e9;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
            }}
            .action-box .icon {{
                font-size: 32px;
                margin-bottom: 10px;
            }}
            .button {{
                display: inline-block;
                padding: 14px 32px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                margin: 15px 0;
                text-align: center;
            }}
            .button:hover {{
                opacity: 0.9;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
                border-top: 1px solid #e9ecef;
                margin-top: 30px;
            }}
            @media only screen and (max-width: 600px) {{
                .info-row {{
                    flex-direction: column;
                }}
                .info-label {{
                    margin-bottom: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-icon">❌</div>
                <h1>Reservation Cancelled</h1>
            </div>
            
            <div class="content">
                <p>Hello <strong>{customer_name}</strong>,</p>
                <p>{main_message}</p>
                
                <div style="text-align: center;">
                    <span class="status-badge">✗ CANCELLED</span>
                </div>
                
                <div class="info-box">
                    <h3>Cancelled Reservation Details</h3>
                    <div class="info-row">
                        <div class="info-label">Reservation ID:</div>
                        <div class="info-value">{reservation_id}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Date & Time:</div>
                        <div class="info-value">{formatted_date_time}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Number of Guests:</div>
                        <div class="info-value">{number_of_guests}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Location:</div>
                        <div class="info-value">{outlet_name}</div>
                    </div>
                    {f'''<div class="info-row">
                        <div class="info-label">Cancellation Reason:</div>
                        <div class="info-value">{cancellation_reason}</div>
                    </div>''' if cancellation_reason else ''}
                </div>
                
                <div class="action-box">
                    <div class="icon">📅</div>
                    <p style="margin: 0; font-weight: 600; color: #0c4a6e; font-size: 18px;">Make a New Reservation</p>
                    <p style="margin: 10px 0; color: #075985;">
                        {closing_message}
                    </p>
                    {f'''<a href="{new_booking_link}" class="button">Book Again</a>''' if new_booking_link else ''}
                </div>
                
                <p style="margin-top: 30px;">If you have any questions or need assistance, please don't hesitate to contact us.</p>
                
                <p style="margin-top: 20px;">Best regards,<br>
                <strong>{brand_name} Team</strong></p>
            </div>
            
            <div class="footer">
                <p style="margin: 5px 0;">© {datetime.now().year} {brand_name}. All rights reserved.</p>
                <p style="margin: 5px 0; font-size: 12px;">This is an automated notification. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
Hello {customer_name},

{main_message.replace('<strong>', '').replace('</strong>', '')}

✗ RESERVATION CANCELLED

CANCELLED RESERVATION DETAILS:
- Reservation ID: {reservation_id}
- Date & Time: {formatted_date_time}
- Number of Guests: {number_of_guests}
- Location: {outlet_name}
{f'- Cancellation Reason: {cancellation_reason}' if cancellation_reason else ''}

📅 MAKE A NEW RESERVATION
{closing_message}

{f'Book again: {new_booking_link}' if new_booking_link else ''}

If you have any questions or need assistance, please don't hesitate to contact us.

Best regards,
{brand_name} Team

---
© {datetime.now().year} {brand_name}. All rights reserved.
This is an automated notification. Please do not reply to this email.
    """

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return JsonResponse({"status": "success", "email": user_email})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def ecosuite_payment_pending_notification(request):
    """
    Send notification when a payment is pending for an Ecosuite reservation.
    Provides a branded email with payment information and CTA.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Required fields
    user_email = data.get("email")
    customer_name = data.get("customerName")
    payment_url = data.get("paymentUrl")

    if not user_email or not customer_name:
        return JsonResponse({"error": "Missing required fields: email and customerName"}, status=400)

    if not payment_url:
        return JsonResponse({"error": "Missing required field: paymentUrl"}, status=400)

    # Optional fields with defaults
    reservation_id = data.get("reservationId") or "N/A"
    amount = data.get("amount") or "N/A"
    outlet_name = data.get("outletName") or "Our Restaurant"
    brand_name = data.get("brandName") or "Tara Tech"
    payment_deadline = data.get("paymentDeadline") or "within the next 24 hours"
    payment_time = data.get("paymentTime") or datetime.utcnow().isoformat()
    notes = data.get("notes") or None

    formatted_payment_time = payment_time
    try:
        if 'T' in payment_time:
            dt = datetime.fromisoformat(payment_time.replace('Z', '+00:00'))
            formatted_payment_time = dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        formatted_payment_time = payment_time.replace('T', ' ').replace('Z', '')

    subject = f"Payment Pending - Reservation {reservation_id}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
            }}
            .header {{
                text-align: center;
                padding: 30px 20px;
                background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
                color: white;
                border-radius: 10px 10px 0 0;
            }}
            .header-icon {{
                font-size: 60px;
                margin-bottom: 10px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .status-badge {{
                display: inline-block;
                background-color: #e0f2fe;
                color: #0369a1;
                padding: 10px 24px;
                border-radius: 999px;
                font-weight: 600;
                margin: 20px 0;
            }}
            .info-box {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #0ea5e9;
            }}
            .info-row {{
                display: flex;
                padding: 10px 0;
                border-bottom: 1px solid #e9ecef;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                flex: 0 0 150px;
                font-weight: 600;
                color: #555;
            }}
            .info-value {{
                flex: 1;
                color: #111;
            }}
            .button {{
                display: inline-block;
                padding: 16px 32px;
                background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                margin: 20px 0;
                text-align: center;
            }}
            .button:hover {{
                opacity: 0.9;
            }}
            .warning-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 13px;
                border-top: 1px solid #e9ecef;
                margin-top: 30px;
            }}
            @media only screen and (max-width: 600px) {{
                .info-row {{
                    flex-direction: column;
                }}
                .info-label {{
                    margin-bottom: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-icon">💳</div>
                <h1>Payment Pending</h1>
            </div>
            
            <div class="content">
                <p>Hello <strong>{customer_name}</strong>,</p>
                <p>We noticed that your reservation payment is still pending. Please complete the payment to secure your booking.</p>
                
                <div style="text-align: center;">
                    <span class="status-badge">Payment Required</span>
                </div>
                
                <div class="info-box">
                    <div class="info-row">
                        <div class="info-label">Reservation ID</div>
                        <div class="info-value">{reservation_id}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Amount Due</div>
                        <div class="info-value">{amount}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Outlet</div>
                        <div class="info-value">{outlet_name}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Requested At</div>
                        <div class="info-value">{formatted_payment_time}</div>
                    </div>
                    {f'''<div class="info-row">
                        <div class="info-label">Notes</div>
                        <div class="info-value">{notes}</div>
                    </div>''' if notes else ''}
                </div>
                
                <div style="text-align: center;">
                    <a href="{payment_url}" class="button">Complete Payment</a>
                </div>
                
                <p style="text-align: center; font-size: 14px; color: #666;">Or copy this link: 
                    <span style="color: #0ea5e9; word-break: break-all;">{payment_url}</span>
                </p>
                
                <div class="warning-box">
                    <p style="margin: 0;"><strong>⏰ Important:</strong> Please complete your payment {payment_deadline} to keep your reservation. The payment link may expire afterwards.</p>
                </div>
                
                <p style="margin-top: 30px;">If you have already completed your payment, please ignore this message.</p>
                
                <p style="margin-top: 20px;">Thank you for choosing <strong>{brand_name}</strong>!</p>
            </div>
            
            <div class="footer">
                <p style="margin: 5px 0;">© {datetime.now().year} {brand_name}. All rights reserved.</p>
                <p style="margin: 5px 0;">This is an automated notification. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
Hello {customer_name},

We noticed that your reservation payment is still pending. Please complete the payment to secure your booking.

Reservation Details:
- Reservation ID: {reservation_id}
- Amount Due: {amount}
- Outlet: {outlet_name}
- Payment Requested At: {formatted_payment_time}
{f'- Notes: {notes}' if notes else ''}

Complete your payment: {payment_url}

Important: Please complete your payment {payment_deadline} to keep your reservation. The payment link may expire afterwards.

If you have already completed your payment, please ignore this message.

Thank you for choosing {brand_name}!

---
© {datetime.now().year} {brand_name}. All rights reserved.
This is an automated notification. Please do not reply to this email.
    """

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return JsonResponse({"status": "success", "email": user_email})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def nocan_send_driver_welcome_message(request):
    """
    Send welcome message to drivers joining the Mens Health Driver Program.
    Includes information about exclusive prizes and events, with a link to the driver dashboard.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Required fields
    user_email = data.get("email")
    driver_name = data.get("driverName") or data.get("name") or "Driver"
    
    if not user_email:
        return JsonResponse({"error": "Missing required field: email"}, status=400)

    driver_dashboard_url = "https://menshealth.id/#/driver"

    subject = "Welcome to the Mens Health Driver Program"
    
    # HTML content with modern styling
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
            }}
            .header {{
                text-align: center;
                padding: 30px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px 10px 0 0;
            }}
            .header-icon {{
                font-size: 64px;
                margin-bottom: 10px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 32px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .welcome-box {{
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border-left: 4px solid #10b981;
                padding: 25px;
                border-radius: 10px;
                margin: 20px 0;
            }}
            .welcome-box .icon {{
                font-size: 32px;
                margin-bottom: 15px;
            }}
            .benefits-box {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }}
            .benefits-box h3 {{
                margin: 0 0 15px 0;
                color: #667eea;
                font-size: 18px;
            }}
            .benefits-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            .benefits-list li {{
                padding: 10px 0;
                padding-left: 30px;
                position: relative;
            }}
            .benefits-list li:before {{
                content: "🎁";
                position: absolute;
                left: 0;
            }}
            .button {{
                display: inline-block;
                padding: 16px 32px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                margin: 20px 0;
                text-align: center;
                font-size: 16px;
            }}
            .button:hover {{
                opacity: 0.9;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
                border-top: 1px solid #e9ecef;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-icon">🚗</div>
                <h1>Welcome to the Driver Program!</h1>
            </div>
            
            <div class="content">
                <p>Hello <strong>{driver_name}</strong>,</p>
                <p>Welcome to the <strong>Mens Health Driver Program</strong>! We're excited to have you join our community of drivers.</p>
                
                <div class="welcome-box">
                    <div class="icon">🎉</div>
                    <p style="margin: 0; font-weight: 600; color: #065f46; font-size: 18px;">Get a chance to win exclusive prizes and be invited to exclusive events!</p>
                </div>
                
                <div class="benefits-box">
                    <h3>What's in it for you?</h3>
                    <ul class="benefits-list">
                        <li>Win exclusive prizes through our driver program</li>
                        <li>Get invited to exclusive events</li>
                        <li>Access your driver dashboard anytime</li>
                        <li>Track your progress and achievements</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{driver_dashboard_url}" class="button">Go to Driver Dashboard</a>
                </div>
                
                <p style="text-align: center; font-size: 14px; color: #666;">
                    Or copy this link: <span style="color: #667eea; word-break: break-all;">{driver_dashboard_url}</span>
                </p>
                
                <p style="margin-top: 30px;">We're thrilled to have you on board and look forward to seeing you at our exclusive events!</p>
                
                <p style="margin-top: 20px;">Best regards,<br>
                <strong>Mens Health Driver Program Team</strong></p>
            </div>
            
            <div class="footer">
                <p style="margin: 5px 0;">© {datetime.now().year} Mens Health. All rights reserved.</p>
                <p style="margin: 5px 0; font-size: 12px;">This is an automated notification. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
Hello {driver_name},

Welcome to the Mens Health Driver Program! We're excited to have you join our community of drivers.

Get a chance to win exclusive prizes and be invited to exclusive events!

What's in it for you?
- Win exclusive prizes through our driver program
- Get invited to exclusive events
- Access your driver dashboard anytime
- Track your progress and achievements

Go to your driver dashboard: {driver_dashboard_url}

We're thrilled to have you on board and look forward to seeing you at our exclusive events!

Best regards,
Mens Health Driver Program Team

---
© {datetime.now().year} Mens Health. All rights reserved.
This is an automated notification. Please do not reply to this email.
    """

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return JsonResponse({"status": "success", "email": user_email})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def ecosuite_send_large_party_reservation_notification(request):
    """
    Send notification to restaurant staff when a large party reservation is made.
    This alerts the restaurant about bookings with a high number of guests.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Required fields
    user_email = data.get("email")  # Restaurant email to notify
    customer_name = data.get("customerName")
    
    # Optional fields with defaults
    reservation_id = data.get("reservationId") or "N/A"
    reservation_date_time = data.get("reservationDateTime") or "N/A"
    number_of_guests = data.get("numberOfGuests") or "N/A"
    outlet_name = data.get("outletName") or "Our Restaurant"
    brand_name = data.get("brandName") or "Tara Tech"
    customer_phone = data.get("customerPhone") or "N/A"
    customer_email = data.get("customerEmail") or "N/A"
    notes = data.get("notes") or None

    if not user_email or not customer_name:
        return JsonResponse({"error": "Missing required fields: email and customerName"}, status=400)

    # Format the date/time if it's in ISO format
    formatted_date_time = reservation_date_time
    try:
        if 'T' in reservation_date_time:
            dt = datetime.fromisoformat(reservation_date_time.replace('Z', '+00:00'))
            formatted_date_time = dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        formatted_date_time = reservation_date_time.replace('T', ' ').replace('Z', '')

    subject = f"Large Party Reservation Alert - {number_of_guests} Guests - {brand_name}"
    
    # HTML content with modern styling
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                color: #ffffff;
                padding: 30px 20px;
                text-align: center;
            }}
            .header-icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .alert-badge {{
                display: inline-block;
                background-color: #fff3cd;
                color: #856404;
                padding: 10px 24px;
                border-radius: 999px;
                font-weight: 600;
                margin: 20px 0;
                border: 2px solid #ffc107;
            }}
            .info-box {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #ff6b6b;
            }}
            .info-row {{
                display: flex;
                padding: 10px 0;
                border-bottom: 1px solid #e9ecef;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                flex: 0 0 150px;
                font-weight: 600;
                color: #555;
            }}
            .info-value {{
                flex: 1;
                color: #111;
            }}
            .highlight-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 13px;
                border-top: 1px solid #e9ecef;
                margin-top: 30px;
            }}
            @media only screen and (max-width: 600px) {{
                .info-row {{
                    flex-direction: column;
                }}
                .info-label {{
                    margin-bottom: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-icon">👥</div>
                <h1>Large Party Reservation Alert</h1>
            </div>
            
            <div class="content">
                <p>Hello Restaurant Team,</p>
                <p>A <strong>large party reservation</strong> has been received and requires your attention.</p>
                
                <div style="text-align: center;">
                    <span class="alert-badge">{number_of_guests} Guests</span>
                </div>
                
                <div class="info-box">
                    <div class="info-row">
                        <div class="info-label">Reservation ID</div>
                        <div class="info-value">{reservation_id}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Customer Name</div>
                        <div class="info-value">{customer_name}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Customer Phone</div>
                        <div class="info-value">{customer_phone}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Customer Email</div>
                        <div class="info-value">{customer_email}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Date & Time</div>
                        <div class="info-value">{formatted_date_time}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Number of Guests</div>
                        <div class="info-value"><strong>{number_of_guests}</strong></div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Outlet</div>
                        <div class="info-value">{outlet_name}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Brand</div>
                        <div class="info-value">{brand_name}</div>
                    </div>
                    {f'''<div class="info-row">
                        <div class="info-label">Notes</div>
                        <div class="info-value">{notes}</div>
                    </div>''' if notes else ''}
                </div>
                
                <div class="highlight-box">
                    <p style="margin: 0;"><strong>⚠️ Action Required:</strong> Please review this large party reservation and ensure adequate preparation for {number_of_guests} guests on {formatted_date_time}.</p>
                </div>
                
                <p style="margin-top: 30px;">Please contact the customer if you need any additional information or have special arrangements to discuss.</p>
                
                <p style="margin-top: 20px;">Thank you for your attention!</p>
            </div>
            
            <div class="footer">
                <p style="margin: 5px 0;">© {datetime.now().year} {brand_name}. All rights reserved.</p>
                <p style="margin: 5px 0;">This is an automated notification from the reservation system.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
Large Party Reservation Alert

Hello Restaurant Team,

A large party reservation has been received and requires your attention.

Reservation Details:
- Reservation ID: {reservation_id}
- Customer Name: {customer_name}
- Customer Phone: {customer_phone}
- Customer Email: {customer_email}
- Date & Time: {formatted_date_time}
- Number of Guests: {number_of_guests}
- Outlet: {outlet_name}
- Brand: {brand_name}
{f'- Notes: {notes}' if notes else ''}

⚠️ Action Required: Please review this large party reservation and ensure adequate preparation for {number_of_guests} guests on {formatted_date_time}.

Please contact the customer if you need any additional information or have special arrangements to discuss.

Thank you for your attention!

---
© {datetime.now().year} {brand_name}. All rights reserved.
This is an automated notification from the reservation system.
    """

    try:
        print(f"Sending large party reservation notification email to {user_email}")
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[user_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"Large party reservation notification sent successfully to {user_email}")
        return JsonResponse({"status": "success", "email": user_email})
    except Exception as e:
        print(f"Error sending large party reservation notification: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)