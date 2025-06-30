from django.urls import path
from .views import CreatePaymentView

urlpatterns = [
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
]