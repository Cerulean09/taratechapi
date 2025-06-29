import json
import uuid
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .paymentService import harsyaPaymentService
from .apiViews import createApiResponse
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def createPayment(request):
    """Create a new payment - called when user clicks 'Pay Online'"""
    try:
        body = json.loads(request.body)
        amount = body.get('amount')
        paymentMethod = body.get('paymentMethod')  # 'virtualAccount' or 'qris'
        receiptId = body.get('receiptId')
        bookingId = body.get('bookingId')
        
        if not amount or not paymentMethod:
            return createApiResponse(False, None, "Amount and payment method are required", 400)
        
        # Get access token
        accessToken = harsyaPaymentService.getToken()
        if not accessToken:
            return createApiResponse(False, None, "Failed to get payment gateway access token", 500)
        
        # Check payment method configuration
        configResponse = harsyaPaymentService.getPaymentMethodConfig(accessToken)
        if not configResponse:
            return createApiResponse(False, None, "Failed to get payment method configuration", 500)
        
        # Generate unique IDs
        invoiceNo = str(uuid.uuid4())
        clientReferenceId = str(uuid.uuid4())
        
        # Prepare payment method objects based on the selected method
        if paymentMethod == 'virtualAccount':
            paymentMethodObject = {"type": "VIRTUAL_ACCOUNT"}
            paymentMethodOptions = {
                "virtualAccount": {
                    "channel": "PERMATA",
                    "virtualAccountName": "Reforza Harsya"
                }
            }
            expiryAt = (datetime.now() + timedelta(days=1)).isoformat()
        elif paymentMethod == 'qris':
            paymentMethodObject = {"type": "QR"}
            paymentMethodOptions = {
                "qr": {
                    "expiryAt": (datetime.now() + timedelta(minutes=30)).isoformat()
                }
            }
            expiryAt = (datetime.now() + timedelta(minutes=30)).isoformat()
        else:
            return createApiResponse(False, None, "Invalid payment method", 400)
        
        # Create metadata
        metadata = {
            "invoiceNo": invoiceNo,
            "receiptId": receiptId,
            "bookingId": bookingId,
            "createdAt": datetime.now().isoformat()
        }
        
        # Create payment
        response = harsyaPaymentService.createPayment(
            accessToken=accessToken,
            invoiceNo=invoiceNo,
            amount=float(amount),
            paymentMethodObject=paymentMethodObject,
            paymentMethodOptions=paymentMethodOptions,
            clientReferenceId=clientReferenceId,
            mode="REDIRECT",
            redirectUrl=None,
            autoConfirm=True,
            statementDescriptor="Harsya",
            expiryAt=expiryAt,
            metadata=metadata
        )
        
        if not response:
            return createApiResponse(False, None, "Failed to create payment", 500)
        
        # Parse the response
        responseData = json.loads(response)
        if responseData.get('code') != '00' or not responseData.get('data'):
            return createApiResponse(False, None, f"Payment creation failed: {responseData.get('message', 'Unknown error')}", 500)
        
        paymentData = responseData['data']
        paymentId = paymentData.get('id')
        
        # Extract payment details based on method
        chargeDetails = paymentData.get('chargeDetails', [])
        paymentDetails = {}
        
        if chargeDetails:
            chargeDetail = chargeDetails[0]
            if paymentMethod == 'virtualAccount' and chargeDetail.get('virtualAccount'):
                vaDetails = chargeDetail['virtualAccount']
                paymentDetails = {
                    "virtualAccountNumber": vaDetails.get('virtualAccountNumber'),
                    "virtualAccountName": vaDetails.get('virtualAccountName'),
                    "channel": vaDetails.get('channel'),
                    "expiryAt": vaDetails.get('expiryAt')
                }
            elif paymentMethod == 'qris' and chargeDetail.get('qr'):
                qrDetails = chargeDetail['qr']
                paymentDetails = {
                    "qrContent": qrDetails.get('qrContent'),
                    "qrUrl": qrDetails.get('qrUrl'),
                    "merchantName": qrDetails.get('merchantName'),
                    "expiryAt": qrDetails.get('expiryAt')
                }
        
        # Return the payment data
        result = {
            "paymentId": paymentId,
            "amount": amount,
            "currency": "IDR",
            "paymentMethod": paymentMethod,
            "status": paymentData.get('status', 'PENDING'),
            "expiryAt": expiryAt,
            "paymentDetails": paymentDetails,
            "paymentUrl": f"/payment/{paymentId}"  # This would be your app's payment URL
        }
        
        return createApiResponse(True, result, "Payment created successfully")
        
    except json.JSONDecodeError:
        return createApiResponse(False, None, "Invalid JSON in request body", 400)
    except Exception as e:
        logger.error(f"Create payment error: {str(e)}")
        return createApiResponse(False, None, f"Error creating payment: {str(e)}", 500)

@csrf_exempt
@require_http_methods(["GET"])
def getPaymentStatus(request, paymentId):
    """Get payment status - called by payment status screen"""
    try:
        if not paymentId:
            return createApiResponse(False, None, "Payment ID is required", 400)
        
        # Get access token
        accessToken = harsyaPaymentService.getToken()
        if not accessToken:
            return createApiResponse(False, None, "Failed to get payment gateway access token", 500)
        
        # Get payment details
        response = harsyaPaymentService.getPaymentDetails(paymentId, accessToken)
        if not response:
            return createApiResponse(False, None, "Failed to get payment details", 500)
        
        # Parse the response
        responseData = json.loads(response)
        if responseData.get('code') != '00' or not responseData.get('data'):
            return createApiResponse(False, None, f"Failed to get payment details: {responseData.get('message', 'Unknown error')}", 500)
        
        paymentData = responseData['data']
        status = paymentData.get('status', 'PENDING')
        
        # Extract payment details
        chargeDetails = paymentData.get('chargeDetails', [])
        paymentDetails = {}
        paymentMethodType = None
        
        if chargeDetails:
            chargeDetail = chargeDetails[0]
            if chargeDetail.get('virtualAccount'):
                paymentMethodType = 'virtualAccount'
                vaDetails = chargeDetail['virtualAccount']
                paymentDetails = {
                    "virtualAccountNumber": vaDetails.get('virtualAccountNumber'),
                    "virtualAccountName": vaDetails.get('virtualAccountName'),
                    "channel": vaDetails.get('channel'),
                    "expiryAt": vaDetails.get('expiryAt')
                }
            elif chargeDetail.get('qr'):
                paymentMethodType = 'qris'
                qrDetails = chargeDetail['qr']
                paymentDetails = {
                    "qrContent": qrDetails.get('qrContent'),
                    "qrUrl": qrDetails.get('qrUrl'),
                    "merchantName": qrDetails.get('merchantName'),
                    "expiryAt": qrDetails.get('expiryAt')
                }
        
        # Determine status message
        statusMessage = "Awaiting payment..."
        if status in ['SUCCESS', 'PAID']:
            statusMessage = "Payment completed successfully"
        elif status in ['FAILED', 'EXPIRED']:
            statusMessage = "Payment failed or expired"
        
        # Calculate time remaining if expiry is set
        timeRemaining = None
        if paymentDetails.get('expiryAt'):
            try:
                expiryTime = datetime.fromisoformat(paymentDetails['expiryAt'].replace('Z', '+00:00'))
                now = datetime.now(expiryTime.tzinfo)
                timeDiff = expiryTime - now
                
                if timeDiff.total_seconds() > 0:
                    hours = int(timeDiff.total_seconds() // 3600)
                    minutes = int((timeDiff.total_seconds() % 3600) // 60)
                    seconds = int(timeDiff.total_seconds() % 60)
                    timeRemaining = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    timeRemaining = "Expired"
            except Exception as e:
                logger.error(f"Error calculating time remaining: {str(e)}")
        
        # Return the payment status
        result = {
            "paymentId": paymentId,
            "status": status,
            "statusMessage": statusMessage,
            "amount": paymentData.get('amount', {}).get('value'),
            "currency": paymentData.get('amount', {}).get('currency', 'IDR'),
            "paymentMethodType": paymentMethodType,
            "paymentDetails": paymentDetails,
            "timeRemaining": timeRemaining,
            "isExpired": timeRemaining == "Expired" if timeRemaining else False,
            "lastChecked": datetime.now().isoformat()
        }
        
        return createApiResponse(True, result, "Payment status retrieved successfully")
        
    except Exception as e:
        logger.error(f"Get payment status error: {str(e)}")
        return createApiResponse(False, None, f"Error getting payment status: {str(e)}", 500)

@csrf_exempt
@require_http_methods(["POST"])
def simulatePayment(request, paymentId):
    """Simulate payment success (for testing purposes)"""
    try:
        if not paymentId:
            return createApiResponse(False, None, "Payment ID is required", 400)
        
        # Get access token
        accessToken = harsyaPaymentService.getToken()
        if not accessToken:
            return createApiResponse(False, None, "Failed to get payment gateway access token", 500)
        
        # Get payment details first to determine payment method
        response = harsyaPaymentService.getPaymentDetails(paymentId, accessToken)
        if not response:
            return createApiResponse(False, None, "Failed to get payment details", 500)
        
        responseData = json.loads(response)
        if responseData.get('code') != '00' or not responseData.get('data'):
            return createApiResponse(False, None, "Failed to get payment details", 500)
        
        paymentData = responseData['data']
        chargeDetails = paymentData.get('chargeDetails', [])
        
        if not chargeDetails:
            return createApiResponse(False, None, "No charge details found", 500)
        
        chargeDetail = chargeDetails[0]
        
        # Determine payment method objects
        if chargeDetail.get('virtualAccount'):
            paymentMethodObject = {"type": "VIRTUAL_ACCOUNT"}
            paymentMethodOptions = {
                "virtualAccount": {
                    "channel": chargeDetail['virtualAccount'].get('channel'),
                    "virtualAccountName": chargeDetail['virtualAccount'].get('virtualAccountName')
                }
            }
        elif chargeDetail.get('qr'):
            paymentMethodObject = {"type": "QR"}
            qrDetails = chargeDetail['qr']
            paymentMethodOptions = {
                "qr": {
                    "expiryAt": qrDetails.get('expiryAt'),
                    "merchantName": qrDetails.get('merchantName'),
                    "qrContent": qrDetails.get('qrContent'),
                    "qrUrl": qrDetails.get('qrUrl')
                }
            }
        else:
            return createApiResponse(False, None, "Unsupported payment method", 500)
        
        # Simulate successful payment
        success = harsyaPaymentService.confirmPayment(
            paymentId=paymentId,
            accessToken=accessToken,
            paymentMethodObject=paymentMethodObject,
            paymentMethodOptions=paymentMethodOptions,
            simulateSuccessPayment=True
        )
        
        if success:
            return createApiResponse(True, {"simulated": True}, "Payment simulated successfully")
        else:
            return createApiResponse(False, None, "Failed to simulate payment", 500)
        
    except Exception as e:
        logger.error(f"Simulate payment error: {str(e)}")
        return createApiResponse(False, None, f"Error simulating payment: {str(e)}", 500) 