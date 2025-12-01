
from django.urls import path
from .views import *

urlpatterns = [
    path('trail-login/', trail_login, name='trail_login'),
    path('login-koala-plus/', login_koala_plus, name='login_koala_plus'),
    path('refresh-access-token/', refresh_access_token, name='refresh_access_token'),
    path('broadcast-templates/', get_broadcast_templates, name='get_broadcast_templates'),
    path('broadcast-otp/', broadcast_otp, name='broadcast_otp'),
    path('trial-broadcast-templates/', trial_get_broadcast_templates, name='trial_get_broadcast_templates'),
]