from django.urls import path
from .views import get_all_contacts

urlpatterns = [
    path("get-all-contacts/", get_all_contacts, name="get_all_contacts"),

]
