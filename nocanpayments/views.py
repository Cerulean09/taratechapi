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
            
class CheckPaymentView(APIView):
    def post(self, request):
        check_payment_url = os.getenv('NOCAN_CHECK_PAYMENT_URL').format(paymentId=request.headers.get('paymentID'))
        access_token_url = os.getenv('NOCAN_ACCESS_TOKEN_URL')
        payment_api_key = os.getenv('NOCAN_PAYMENT_API_KEY')
        payment_api_secret = os.getenv('NOCAN_PAYMENT_API_SECRET')

        # Step 1: Get access token
        token_headers = {
            'X-MERCHANT-ID': payment_api_key,
            'X-MERCHANT-SECRET': payment_api_secret,
            'Content-Type': 'application/json',
        }

        token_response = requests.post(access_token_url, headers=token_headers, json={
            "grantType": "client_credentials"
        })

        try:
            access_token = token_response.json()['data']['accessToken']
        except Exception as e:
            return Response({
                "error": "Failed to parse token response",
                "response_text": token_response.text,
                "status_code": token_response.status_code
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Forward the Flutter payload
        forward_headers = {
            'Authorization': f'Bearer {access_token}',
            'X-MERCHANT-ID': payment_api_key,
            'X-MERCHANT-SECRET': payment_api_secret,
            'Content-Type': 'application/json',
        }

        gateway_response = requests.get(check_payment_url, headers=forward_headers)
        return Response(gateway_response.json(), status=gateway_response.status_code)


        
class CreatePaymentView(APIView):
    def post(self, request):
        try:
            create_payment_url = os.getenv('NOCAN_CREATE_PAYMENT_URL')
            access_token_url = os.getenv('NOCAN_ACCESS_TOKEN_URL')
            payment_api_key = os.getenv('NOCAN_PAYMENT_API_KEY')
            payment_api_secret = os.getenv('NOCAN_PAYMENT_API_SECRET')

            if not all([create_payment_url, access_token_url, payment_api_key, payment_api_secret]):
                return Response({
                    "error": "Missing environment variables"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Step 1: Get access token
            token_headers = {
                'X-MERCHANT-ID': payment_api_key,
                'X-MERCHANT-SECRET': payment_api_secret,
                'Content-Type': 'application/json',
            }

            token_response = requests.post(access_token_url, headers=token_headers, json={
                "grantType": "client_credentials"
            })

            try:
                access_token = token_response.json()['data']['accessToken']
            except Exception as e:
                return Response({
                    "error": "Failed to parse token response",
                    "response_text": token_response.text,
                    "status_code": token_response.status_code
                }, status=status.HTTP_400_BAD_REQUEST)

            # Step 2: Forward the Flutter payload
            forward_headers = {
                'Authorization': f'Bearer {access_token}',
                'X-MERCHANT-ID': payment_api_key,
                'X-MERCHANT-SECRET': payment_api_secret,
                'Content-Type': 'application/json',
            }

            gateway_response = requests.post(
                create_payment_url,
                headers=forward_headers,
                json=request.data  # 🔥 forwarding Flutter body as-is
            )

            try:
                return Response(gateway_response.json(), status=gateway_response.status_code)
            except Exception as e:
                return Response({
                    "error": "Gateway did not return JSON",
                    "status_code": gateway_response.status_code,
                    "raw": gateway_response.text,
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": "Internal server error",
                "details": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        