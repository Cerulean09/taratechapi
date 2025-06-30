from django.urls import path, include
from .views import CreatePaymentView

urlpatterns = [
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('confirm-payment/', ConfirmPaymentView.as_view(), name='confirm-payment'),
]