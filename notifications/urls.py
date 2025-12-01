from django.urls import path
from .views import *

urlpatterns = [
    path("send-login-notification/", send_login_notification, name="send_login_notification"),

    path("send-signup-notification/", send_signup_notification, name="send_signup_notification"),

    path("send-reservation-request-notification/", send_reservation_request_notification, name="send_reservation_request_notification"),

    path("send-reservation-confirmation-notification/", send_reservation_confirmation_notification, name="send_reservation_confirmation_notification"),

    path("send-reservation-cancellation-notification/", send_reservation_cancellation_notification, name="send_reservation_cancellation_notification"),

    path("send-payment-pending-notification/", send_payment_pending_notification, name="send_payment_pending_notification"),

    path("send-forgot-password-otp-notification/", send_forgot_password_otp_notification, name="send_forgot_password_otp_notification"),
    
    # Nocan Endpoints
    path("nocan-send-driver-welcome-message/", nocan_send_driver_welcome_message, name="nocan_send_driver_welcome_message"),
    
    # Ecosuite Endpoints
    path("ecosuite-on-hold-notification/", ecosuite_on_hold_notification, name="ecosuite_on_hold_notification"),
    
    path("ecosuite-confirmed-status/", ecosuite_confirmed_status, name="ecosuite_confirmed_status"),
    
    path("ecosuite-cancelled-notification/", ecosuite_cancelled_notification, name="ecosuite_cancelled_notification"),

    path("ecosuite-payment-pending-notification/", ecosuite_payment_pending_notification, name="ecosuite_payment_pending_notification"),
    
    path("ecosuite-send-large-party-reservation-notification/", ecosuite_send_large_party_reservation_notification, name="ecosuite_send_large_party_reservation_notification"),
]
