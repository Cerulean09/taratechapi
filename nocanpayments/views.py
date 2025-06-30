from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import os

# Create your views here.

class CreatePaymentView(APIView):
    def post(self, request):
        #! REPLACE WITH YOUR PAYMENT GATEWAY URL
        payment_gateway_url = 'REPLACE WITH YOUR PAYMENT GATEWAY URL'
        payment_api_key = os.getenv('NOCAN_PAYMENT_API_KEY')
        payment_api_secret = os.getenv('NOCAN_PAYMENT_API_SECRET')
        
        amount = request.data.get('amount')
        customer_name = request.data.get('name')
        

        # prepare request to your payment gateway
        gateway_payload = {
            'amount': amount,
            'customer_name': customer_name,
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("PAYMENT_GATEWAY_API_KEY")}',
        }

        try:
            response = requests.post(payment_gateway_url, json=gateway_payload, headers=headers)
            response.raise_for_status()
            payment_data = response.json()

            return Response(payment_data, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({
                'error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
        