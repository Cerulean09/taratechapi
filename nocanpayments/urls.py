from django.urls import path, include
from .views import CreatePaymentView, ConfirmPaymentView, CheckPaymentView, PaymentMethodConfigView

urlpatterns = [
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('confirm-payment/', ConfirmPaymentView.as_view(), name='confirm-payment'),
    path('check-payment/', CheckPaymentView.as_view(), name='check-payment'),
    path('payment-method-config/', PaymentMethodConfigView.as_view(), name='payment-method-config'),
]