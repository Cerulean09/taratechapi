from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import os

# Create your views here.

class ConfirmPaymentView(APIView):
    def post(self, request):
        confirm_payment_url = os.getenv('NOCAN_CONFIRM_PAYMENT_URL').format(paymentId=request.data.get('paymentId'))
        access_token_url = os.getenv('NOCAN_ACCESS_TOKEN_URL')
        payment_api_key = os.getenv('NOCAN_PAYMENT_API_KEY')
        payment_api_secret = os.getenv('NOCAN_PAYMENT_API_SECRET')

        try:
            # request token
            headers = {
                'X-MERCHANT-ID': payment_api_key,
                'X-MERCHANT-SECRET': payment_api_secret,
            }

            response = requests.post(access_token_url, headers=headers, json={  
                "grantType":"client_credentials"
            })
            access_token = response.json()['data']['accessToken']
        
            # prepare request to your payment gateway
            gateway_payload = {
                'paymentMethod': request.data.get('paymentMethod'),
                'paymentMethodOptions': request.data.get('paymentMethodOptions'),
            }

            headers = {
                'Authorization': f'Bearer {access_token}',
                'X-MERCHANT-ID': payment_api_key,
                'X-MERCHANT-SECRET': payment_api_secret,
            }

            try:
                response = requests.post(confirm_payment_url, json=gateway_payload, headers=headers)
                response.raise_for_status()
                payment_data = response.json()

                return Response(payment_data, status=status.HTTP_200_OK)
            except requests.exceptions.RequestException as e:
                return Response({
                    'error': str(e),
                }, status=status.HTTP_400_BAD_REQUEST)
            

            
        except requests.exceptions.RequestException as e:
            return Response({
                'error': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
            

        

class CreatePaymentView(APIView):
    def post(self, request):
        create_payment_url = os.getenv('NOCAN_CREATE_PAYMENT_URL')
        access_token_url = os.getenv('NOCAN_ACCESS_TOKEN_URL')
        payment_api_key = os.getenv('NOCAN_PAYMENT_API_KEY')
        payment_api_secret = os.getenv('NOCAN_PAYMENT_API_SECRET')

        try:
            # request token
            headers = {
                'X-MERCHANT-ID': payment_api_key,
                'X-MERCHANT-SECRET': payment_api_secret,
            }

            response = requests.post(access_token_url, headers=headers, json={
                "grantType":"client_credentials"
            })
            access_token = response.json()['data']['accessToken']


            # prepare request to your payment gateway
            gateway_payload = {
                'clientReferenceId': request.data.get('clientReferenceId'),
                'amount': request.data.get('amount'),
                'paymentMethod': request.data.get('paymentMethod'),
                'paymentMethodOptions': request.data.get('paymentMethodOptions'),
                'metadata': request.data.get('metadata'),
                'mode': request.data.get('mode'),
                'redirectUrl': request.data.get('redirectUrl'),
                "autoConfirm": request.data.get('autoConfirm'),
                "statementDescriptor": request.data.get('statementDescriptor'),
                "expiryAt": request.data.get('expiryAt'),
            }

            headers = {
                'Authorization': f'Bearer {access_token}',
                'X-MERCHANT-ID': payment_api_key,
                'X-MERCHANT-SECRET': payment_api_secret,
            }

            try:
                response = requests.post(create_payment_url, json=gateway_payload, headers=headers)
                response.raise_for_status()
                payment_data = response.json()

                return Response(payment_data, status=status.HTTP_200_OK)
            except requests.exceptions.RequestException as e:
                return Response({
                    'error': str(e+'\n create payment error'),
                }, status=status.HTTP_400_BAD_REQUEST)
            

            
        except requests.exceptions.RequestException as e:
            return Response({
                'error': str(e+'\n token error'),
            }, status=status.HTTP_400_BAD_REQUEST)
            

        