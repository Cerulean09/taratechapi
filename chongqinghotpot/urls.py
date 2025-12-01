from django.urls import path
from .views import *

urlpatterns = [
    path("get-all-whatsapp-templates/", get_all_whatsapp_templates, name="get_all_whatsapp_templates"),
    path("get-all-rooms/", get_all_rooms, name="get_all_rooms"),
    
    # CRM OAuth Flow
    path("crm/login/", crm_login, name="crm_login"),
    path("crm/callback/", crm_callback, name="crm_callback"),
    path("crm/token-status/", crm_token_status, name="crm_token_status"),
    
    # CRM API Endpoints
    path("get-all-contacts/", get_all_contacts, name="get_all_contacts"),
]
