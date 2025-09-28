"""
WSGI config for taratechapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ['NOCAN_CREATE_PAYMENT_URL'] = 'https://api.harsya.com/v2/payments'
os.environ['NOCAN_CONFIRM_PAYMENT_URL'] = 'https://api.harsya.com/v2/payments/{paymentId}/confirm'
os.environ['NOCAN_CHECK_PAYMENT_URL'] = 'https://api.harsya.com/v2/payments/{paymentId}'
os.environ['NOCAN_PAYMENT_METHOD_CONFIG_URL'] = 'https://api.harsya.com/v2/payment-method-configs'
os.environ['NOCAN_ACCESS_TOKEN_URL'] = 'https://api.harsya.com/v1/access-token'
os.environ['NOCAN_PAYMENT_API_KEY'] = 'f723686f-c957-46f6-b530-970222479378'
os.environ['NOCAN_PAYMENT_API_SECRET'] = 'aQtTUNC8R5ZNyZidtURDLL39K0LaMXqgRLjuszm3'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taratechapi.settings')

application = get_wsgi_application()
