# Ecosuite On Hold Notification

## Overview
This notification endpoint sends a beautifully designed email to customers when their reservation is placed on hold, informing them that:
1. Their booking has been received
2. It is currently on hold for them
3. They will receive a confirmation message 2 days before their booking

## Endpoint
```
POST /api/notifications/ecosuite-on-hold-notification/
```

**Authentication**: None required

## Request Format

### Headers
```
Content-Type: application/json
```

### Request Body

#### Required Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `email` | string | Customer email address | "customer@example.com" |
| `customerName` | string | Customer's name | "John Doe" |

#### Optional Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `reservationId` | string | Reservation ID | "abc-123-def-456" |
| `reservationDateTime` | string | ISO datetime or formatted string | "2025-11-20T19:00:00+07:00" |
| `numberOfGuests` | integer | Number of guests | 4 |
| `outletName` | string | Restaurant/outlet name | "Grand Palace Restaurant" |
| `brandName` | string | Brand name | "Fine Dining Co." |
| `notes` | string | Special requests or notes | "Window seat preferred" |
| `confirmationLink` | string | Link to confirmation page | "https://example.com/confirm/abc-123" |

**Note**: If optional fields are not provided, defaults will be used (e.g., "N/A", "Our Restaurant", "Tara Tech")

## Example Requests

### Minimal Request
```bash
curl -X POST https://your-domain.com/api/notifications/ecosuite-on-hold-notification/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "customerName": "John Doe"
  }'
```

### Complete Request
```bash
curl -X POST https://your-domain.com/api/notifications/ecosuite-on-hold-notification/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "customerName": "John Doe",
    "reservationId": "550e8400-e29b-41d4-a716-446655440000",
    "reservationDateTime": "2025-11-20T19:00:00+07:00",
    "numberOfGuests": 4,
    "outletName": "Grand Palace Restaurant",
    "brandName": "Fine Dining Co.",
    "notes": "Window seat preferred, celebrating anniversary",
    "confirmationLink": "https://example.com/api/ecosuite/confirm-reservation/550e8400-e29b-41d4-a716-446655440000/"
  }'
```

### JavaScript/Node.js Example
```javascript
async function sendOnHoldNotification(reservationData) {
  const response = await fetch('https://your-domain.com/api/notifications/ecosuite-on-hold-notification/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: reservationData.customerEmail,
      customerName: reservationData.customerName,
      reservationId: reservationData.id,
      reservationDateTime: reservationData.reservationDateTime,
      numberOfGuests: reservationData.numberOfGuests,
      outletName: reservationData.outletName,
      brandName: reservationData.brandName,
      notes: reservationData.notes,
      confirmationLink: `https://your-domain.com/api/ecosuite/confirm-reservation/${reservationData.id}/`
    })
  });
  
  return await response.json();
}
```

### Python Example
```python
import requests
import json

def send_on_hold_notification(reservation):
    url = "https://your-domain.com/api/notifications/ecosuite-on-hold-notification/"
    
    payload = {
        "email": reservation["customerEmail"],
        "customerName": reservation["customerName"],
        "reservationId": reservation["id"],
        "reservationDateTime": reservation["reservationDateTime"],
        "numberOfGuests": reservation["numberOfGuests"],
        "outletName": reservation.get("outletName", "Our Restaurant"),
        "brandName": reservation.get("brandName", "Tara Tech"),
        "notes": reservation.get("notes"),
        "confirmationLink": f"https://your-domain.com/api/ecosuite/confirm-reservation/{reservation['id']}/"
    }
    
    response = requests.post(url, json=payload)
    return response.json()
```

## Response Format

### Success Response (200 OK)
```json
{
  "status": "success",
  "email": "john@example.com"
}
```

### Error Responses

**Missing Required Fields (400 Bad Request)**
```json
{
  "error": "Missing required fields: email and customerName"
}
```

**Invalid JSON (400 Bad Request)**
```json
{
  "error": "Invalid JSON"
}
```

**Method Not Allowed (405)**
```json
{
  "error": "Only POST allowed"
}
```

**Email Send Failure (500 Internal Server Error)**
```json
{
  "error": "Error message from email service"
}
```

## Email Features

### Visual Design
- 🎉 Celebration emoji header
- Modern gradient purple theme
- Responsive design (mobile-friendly)
- Professional layout with branded colors
- Clear status badge showing "ON HOLD"

### Content Sections

1. **Header**
   - Gradient background with "Booking Received!" message
   - Celebration icon

2. **Greeting**
   - Personalized with customer name
   - Clear message about booking status

3. **Status Badge**
   - Visual indicator showing "⏳ ON HOLD"
   - Yellow/gold color scheme

4. **Reservation Details Box**
   - Reservation ID
   - Formatted date and time
   - Number of guests
   - Location (outlet name)
   - Notes (if provided)

5. **Confirmation Reminder**
   - Blue info box with calendar icon
   - Clear message about 2-day advance confirmation
   - Prominent and easy to understand

6. **Confirmation Link** (if provided)
   - Styled button to view reservation
   - Fallback text link

7. **Footer**
   - Brand information
   - Copyright notice
   - Automated message disclaimer

### DateTime Formatting
The notification automatically formats ISO datetime strings to a readable format:
- Input: `2025-11-20T19:00:00+07:00`
- Output: `Monday, November 20, 2025 at 07:00 PM`

## Integration with Ecosuite Reservations

### When to Send This Notification

Send this notification when:
1. A reservation status is set to "on hold"
2. Staff manually places a reservation on hold
3. System automatically places a reservation on hold after confirmation

### Integration Example with Reservation Creation

```python
# In ecosuite/views.py - after creating/updating reservation to "on hold"

from django.conf import settings
import requests

def notify_customer_on_hold(reservation):
    """Send on-hold notification to customer"""
    
    # Extract customer email from reservation
    # Assuming you have customer email in the reservation or need to fetch it
    customer_email = reservation.get('customerEmail')
    
    if not customer_email:
        # Try to get from phone number lookup or other means
        customer_email = get_customer_email_from_phone(reservation['customerPhone'])
    
    if not customer_email:
        print(f"No email found for reservation {reservation['id']}")
        return False
    
    # Build confirmation link
    confirmation_link = f"{settings.BASE_URL}/api/ecosuite/confirm-reservation/{reservation['id']}/"
    
    # Prepare notification payload
    notification_data = {
        'email': customer_email,
        'customerName': reservation['customerName'],
        'reservationId': reservation['id'],
        'reservationDateTime': reservation['reservationDateTime'],
        'numberOfGuests': reservation['numberOfGuests'],
        'outletName': get_outlet_name(reservation['outletId']),
        'brandName': get_brand_name(reservation['brandId']),
        'notes': reservation.get('notes'),
        'confirmationLink': confirmation_link
    }
    
    try:
        # Send notification
        response = requests.post(
            f"{settings.BASE_URL}/api/notifications/ecosuite-on-hold-notification/",
            json=notification_data,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send on-hold notification: {e}")
        return False
```

### Update Reservation Status Endpoint

```python
# Example: Add notification to upsert_reservation endpoint

@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def upsert_reservation(request, reservation_id):
    # ... existing code ...
    
    # After successful reservation update/creation
    if response.data:
        reservation = response.data[0]
        
        # Check if status changed to "on hold"
        if reservation['status'] == 'on hold':
            # Send notification
            notify_customer_on_hold(reservation)
        
        return Response({
            "message": "Reservation created/updated successfully",
            "reservation": reservation
        }, status=status.HTTP_200_OK)
```

## Testing

### Test with cURL
```bash
# Test minimal request
curl -X POST http://localhost:8000/api/notifications/ecosuite-on-hold-notification/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "customerName": "Test User"
  }'

# Test complete request
curl -X POST http://localhost:8000/api/notifications/ecosuite-on-hold-notification/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "customerName": "Test User",
    "reservationId": "test-123",
    "reservationDateTime": "2025-12-25T19:00:00+07:00",
    "numberOfGuests": 4,
    "outletName": "Test Restaurant",
    "brandName": "Test Brand",
    "notes": "Test notes",
    "confirmationLink": "https://example.com/confirm/test-123"
  }'
```

### Expected Email Preview
When you send the notification, the customer will receive an email that looks like this:

**Subject**: Booking Received - [Brand Name] Reservation

**Body**:
- Header with celebration emoji and gradient background
- Personalized greeting
- "ON HOLD" status badge
- Detailed reservation information in a styled box
- Blue reminder box about 2-day advance confirmation
- Optional confirmation button
- Professional footer

## Email Service Configuration

Make sure your Django email settings are configured in `settings.py`:

```python
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@yourcompany.com'
```

## Customization

### Change Brand Colors
Edit the HTML content in `notifications/views.py`:
```python
# Change gradient colors
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);

# Change accent color
border-left: 4px solid #YOUR_ACCENT_COLOR;
```

### Modify Confirmation Reminder
Update the reminder text in the `reminder-box` section:
```python
<p style="margin: 10px 0 0 0; color: #1565c0;">
    You will receive a confirmation message <strong>X days before your booking</strong>...
</p>
```

### Add Additional Information
Add new fields to the info-box section:
```python
<div class="info-row">
    <div class="info-label">New Field:</div>
    <div class="info-value">{new_field_value}</div>
</div>
```

## Best Practices

1. **Always Include Confirmation Link**: Makes it easy for customers to view/manage their reservation
2. **Send Immediately**: Send this notification as soon as the reservation is placed on hold
3. **Include All Details**: Provide complete reservation information
4. **Use Brand Name**: Personalize with your brand name
5. **Test Email Delivery**: Ensure your email service is properly configured
6. **Monitor Failures**: Log and monitor failed email sends
7. **Follow-up**: Remember to send the promised confirmation 2 days before the booking

## Automation Workflow

```
Reservation Created/Updated
         ↓
Status = "on hold"?
         ↓
       YES
         ↓
Send On-Hold Notification
         ↓
Customer Receives Email
         ↓
[2 Days Before Booking]
         ↓
Send Confirmation Notification
         ↓
Customer Confirms/Modifies
```

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Email not received | Email configuration issue | Check Django email settings |
| 500 error | SMTP connection failed | Verify SMTP credentials |
| HTML not rendering | Email client issue | Plain text version included as fallback |
| DateTime format issue | Invalid ISO string | Ensure datetime is ISO 8601 format |
| Missing confirmation link | Not provided in request | Add confirmationLink to request payload |

## Support

For questions or issues with this notification:
- Check email service configuration
- Verify all required fields are provided
- Test with a simple request first
- Check server logs for detailed error messages
- Ensure email address is valid and deliverable

## Related Documentation
- `TWO_STEP_RESERVATION_FLOW.md` - Reservation creation flow
- `RESERVATION_CONFIRMATION_ENDPOINT.md` - Confirmation page details
- `RESERVATION_API_QUICK_REFERENCE.md` - API reference





