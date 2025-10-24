from django.urls import path
from .views import send_login_notification, send_signup_notification, send_reservation_request_notification, send_reservation_confirmation_notification, send_reservation_cancellation_notification

urlpatterns = [
    path("send-login-notification/", send_login_notification, name="send_login_notification"),

    path("send-signup-notification/", send_signup_notification, name="send_signup_notification"),

    path("send-reservation-request-notification/", send_reservation_request_notification, name="send_reservation_request_notification"),


    path("send-reservation-confirmation-notification/", send_reservation_confirmation_notification, name="send_reservation_confirmation_notification"),

    path("send-reservation-cancellation-notification/", send_reservation_cancellation_notification, name="send_reservation_cancellation_notification"),
]
