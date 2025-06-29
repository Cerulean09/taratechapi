# Payment API Documentation

This document describes the payment APIs created for the Nocan app to integrate with the Harsya payment gateway, configured for PythonAnywhere deployment.

## 🚀 **Live API Endpoints**

Your APIs are now live at: **https://taratechid.pythonanywhere.com**

### **Available Endpoints:**
- **Base URL:** `https://taratechid.pythonanywhere.com`
- **API Base:** `https://taratechid.pythonanywhere.com/api`
- **Payment API:** `https://taratechid.pythonanywhere.com/api/payment`

## 🛠 **Setup**

### 1. Configure Harsya Payment Gateway

Before using the APIs, you need to configure the Harsya payment gateway credentials in `nocan/paymentService.py`:

```python
class HarsyaPaymentService:
    def __init__(self):
        # Replace these with your actual Harsya API credentials
        self.baseUrl = "https://api.harsya.com"  # Your actual Harsya API URL
        self.clientId = "your_client_id"  # Your actual client ID
        self.clientSecret = "your_client_secret"  # Your actual client secret
```

### 2. URL Configuration

The project uses a centralized URL configuration system. To change URLs, you only need to update **one file**:

**File to update:** `taratechapi/settings.py`

```python
# Change this line to update all URLs
BASE_URL = 'https://taratechid.pythonanywhere.com'  # PythonAnywhere Production
# BASE_URL = 'http://localhost:8000'  # Development
# BASE_URL = 'https://staging.your-domain.com'  # Staging
```

### 3. Using URL Configuration in Your Code

Import and use the URL configuration utility:

```python
from nocan.urlConfig import get_payment_create_url, get_payment_status_url

# Get payment creation URL
create_url = get_payment_create_url()
# Returns: https://taratechid.pythonanywhere.com/api/payment/create/

# Get payment status URL
status_url = get_payment_status_url("pay_123456789")
# Returns: https://taratechid.pythonanywhere.com/api/payment/pay_123456789/status/
```

## 📡 **API Endpoints**

### 1. Create Payment

**Endpoint:** `POST https://taratechid.pythonanywhere.com/api/payment/create/`

**Description:** Creates a new payment when user clicks "Pay Online" in the Flutter app.

**Request Body:**
```json
{
    "amount": 100000,
    "paymentMethod": "virtualAccount",
    "receiptId": "receipt-123",
    "bookingId": "booking-456"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Payment created successfully",
    "data": {
        "paymentId": "pay_123456789",
        "amount": 100000,
        "currency": "IDR",
        "paymentMethod": "virtualAccount",
        "status": "PENDING",
        "expiryAt": "2024-01-01T23:59:59",
        "paymentDetails": {
            "virtualAccountNumber": "1234567890",
            "virtualAccountName": "Reforza Harsya",
            "channel": "PERMATA",
            "expiryAt": "2024-01-01T23:59:59"
        },
        "paymentUrl": "/payment/pay_123456789"
    }
}
```

### 2. Get Payment Status

**Endpoint:** `GET https://taratechid.pythonanywhere.com/api/payment/{paymentId}/status/`

**Description:** Gets the current status of a payment. Used by the payment status screen.

**Response:**
```json
{
    "success": true,
    "message": "Payment status retrieved successfully",
    "data": {
        "paymentId": "pay_123456789",
        "status": "PENDING",
        "statusMessage": "Awaiting payment...",
        "amount": 100000,
        "currency": "IDR",
        "paymentMethodType": "virtualAccount",
        "paymentDetails": {
            "virtualAccountNumber": "1234567890",
            "virtualAccountName": "Reforza Harsya",
            "channel": "PERMATA",
            "expiryAt": "2024-01-01T23:59:59"
        },
        "timeRemaining": "23:59:59",
        "isExpired": false,
        "lastChecked": "2024-01-01T12:00:00"
    }
}
```

### 3. Simulate Payment (Testing)

**Endpoint:** `POST https://taratechid.pythonanywhere.com/api/payment/{paymentId}/simulate/`

**Description:** Simulates a successful payment for testing purposes.

**Response:**
```json
{
    "success": true,
    "message": "Payment simulated successfully",
    "data": {
        "simulated": true
    }
}
```

## 📱 **Integration with Flutter App**

### 1. Update Payment Screen

In your Flutter `payment_screen.dart`, replace the direct Harsya API calls with calls to your PythonAnywhere API:

```dart
// Instead of calling HarsyaPaymentGateway.createPayment directly
// Call your PythonAnywhere API

Future<void> createPayment() async {
  try {
    final response = await http.post(
      Uri.parse('https://taratechid.pythonanywhere.com/api/payment/create/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'amount': currentReceipt.amountDue,
        'paymentMethod': 'virtualAccount', // or 'qris'
        'receiptId': currentReceipt.receiptId,
        'bookingId': widget.id,
      }),
    );

    final data = jsonDecode(response.body);
    if (data['success']) {
      final paymentData = data['data'];
      // Navigate to payment status screen with payment ID
      context.go('/payment/${paymentData['paymentId']}/status');
    }
  } catch (e) {
    // Handle error
  }
}
```

### 2. Update Payment Status Screen

In your Flutter `payment_status_screen.dart`, replace the direct Harsya API calls:

```dart
Future<void> checkPaymentStatus() async {
  try {
    final response = await http.get(
      Uri.parse('https://taratechid.pythonanywhere.com/api/payment/$paymentId/status/'),
    );

    final data = jsonDecode(response.body);
    if (data['success']) {
      final statusData = data['data'];
      setState(() {
        _status = statusData['status'];
        _message = statusData['statusMessage'];
        // Update other UI elements
      });
    }
  } catch (e) {
    // Handle error
  }
}
```

## 🧪 **Testing**

### 1. Test the Live APIs

Use the provided test script:

```bash
python test_payment_api.py
```

Or test manually with curl:

```bash
# Create payment
curl -X POST https://taratechid.pythonanywhere.com/api/payment/create/ \
  -H "Content-Type: application/json" \
  -d '{"amount": 100000, "paymentMethod": "virtualAccount", "receiptId": "test-123", "bookingId": "test-456"}'

# Get payment status (replace PAYMENT_ID with actual ID)
curl https://taratechid.pythonanywhere.com/api/payment/PAYMENT_ID/status/

# Simulate payment (replace PAYMENT_ID with actual ID)
curl -X POST https://taratechid.pythonanywhere.com/api/payment/PAYMENT_ID/simulate/
```

### 2. Test All Endpoints

The test script will automatically test all available endpoints and show you the results.

## 🔧 **URL Management**

### **Single File Configuration**

To change URLs in the future, you only need to update **one line** in `taratechapi/settings.py`:

```python
# Change this line to update all URLs
BASE_URL = 'https://taratechid.pythonanywhere.com'  # Current production URL
```

### **Available URL Functions**

```python
from nocan.urlConfig import (
    get_base_url,           # https://taratechid.pythonanywhere.com
    get_api_base_url,       # https://taratechid.pythonanywhere.com/api
    get_payment_create_url, # https://taratechid.pythonanywhere.com/api/payment/create/
    get_payment_status_url, # https://taratechid.pythonanywhere.com/api/payment/{id}/status/
    get_api_url            # Get any endpoint by name
)
```

## 🚨 **Error Handling**

The APIs return standardized error responses:

```json
{
    "success": false,
    "message": "Error description",
    "data": null
}
```

Common error scenarios:
- Invalid payment method
- Missing required fields
- Harsya API connection issues
- Invalid payment ID

## 🔒 **Security Considerations**

1. **HTTPS**: All endpoints use HTTPS on PythonAnywhere
2. **Authentication**: Consider adding authentication to protect your payment APIs
3. **Input Validation**: The APIs include basic validation, but consider adding more robust validation
4. **Rate Limiting**: Consider implementing rate limiting to prevent abuse
5. **Logging**: All API calls are logged for debugging and monitoring

## 🌍 **Environment Variables**

For production, consider using environment variables for sensitive configuration:

```python
import os

class HarsyaPaymentService:
    def __init__(self):
        self.baseUrl = os.getenv('HARSYA_API_URL', 'https://api.harsya.com')
        self.clientId = os.getenv('HARSYA_CLIENT_ID')
        self.clientSecret = os.getenv('HARSYA_CLIENT_SECRET')
```

## 📞 **Support**

For issues or questions:
1. Check the Django logs for detailed error messages
2. Verify your Harsya API credentials
3. Test with the provided test script
4. Ensure your PythonAnywhere app is running and accessible
5. Check PythonAnywhere error logs in your dashboard

## 🎯 **Quick Reference**

**Live API Base:** `https://taratechid.pythonanywhere.com/api`

**Key Endpoints:**
- Create Payment: `POST /api/payment/create/`
- Get Status: `GET /api/payment/{id}/status/`
- Simulate: `POST /api/payment/{id}/simulate/`

**Configuration File:** `taratechapi/settings.py` (single file to update URLs) 