from django.urls import path
from .views import send_login_notification

urlpatterns = [
    path("send-login-notification/", send_login_notification, name="send_login_notification"),
]
