from django.urls import path
from .views import get_crm_contacts

urlpatterns = [
    path("get-crm-contacts/", get_crm_contacts, name="get_crm_contacts"),

]
