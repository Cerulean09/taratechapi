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
os.environ['ZOHO_EMAIL_USER']='hello@taratech.id'
os.environ['ZOHO_EMAIL_PASS']='ClearDay9'
os.environ['EMAIL_HOST']='smtp.zoho.com'
os.environ['EMAIL_PORT']=465
os.environ['EMAIL_USE_SSL']=1
os.environ['EMAIL_USE_TLS']=0
os.environ['DEFAULT_FROM_EMAIL']='hello@taratech.id'

os.environ['MEKARI_URL'] = 'api.mekari.com'
os.environ['CQ_HOTPOT_QONTAK_CLIENT_ID'] = '4TkGVjzR25cDISZB'
os.environ['CQ_HOTPOT_QONTAK_CLIENT_SECRET'] = 'FgW8fvfoiO3YAXwF1yWbNDXwGhmFROrl'
os.environ['CQ_HOTPOT_QONTAK_ACCESS_TOKEN'] = 'IPqU4f8KB-DMk54E9st0MPVtotZk4rB7Rq3L8eW1_08'
os.environ['CQ_HOTPOT_QONTAK_REFRESH_TOKEN'] = 'uRmTxjVJ-XYQ8didFYr6_KXpiBTceeYyRqIZifkbVdU'

application = get_wsgi_application()
