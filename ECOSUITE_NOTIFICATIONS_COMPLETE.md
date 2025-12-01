# Ecosuite Complete Notification System

## Overview
Complete notification system for Ecosuite reservations with beautiful, branded email templates for all reservation states.

## All Notification Endpoints

| Endpoint | Status | Purpose | Icon | Color Theme |
|----------|--------|---------|------|-------------|
| `/ecosuite-on-hold-notification/` | On Hold | Booking received, on hold | 🎉 | Purple |
| `/ecosuite-confirmed-status/` | Confirmed | Reservation confirmed | ✅ | Green |
| `/ecosuite-cancelled-notification/` | Cancelled | Reservation cancelled | ❌ | Red/Pink |

---

## 1. On Hold Notification

**Endpoint**: `POST /api/notifications/ecosuite-on-hold-notification/`

**When to Send**: When a reservation is placed "on hold" by staff

**Key Message**: Booking received, will get confirmation 2 days before

### Required Fields
- `email` - Customer email
- `customerName` - Customer name

### Optional Fields
- `reservationId`, `reservationDateTime`, `numberOfGuests`, `outletName`, `brandName`, `notes`, `confirmationLink`

### Example Request
```bash
curl -X POST https://api.example.com/notifications/ecosuite-on-hold-notification/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "customerName": "John Doe",
    "reservationId": "abc-123",
    "reservationDateTime": "2025-11-20T19:00:00+07:00",
    "numberOfGuests": 4,
    "outletName": "Grand Palace",
    "brandName": "Fine Dining Co.",
    "notes": "Window seat",
    "confirmationLink": "https://example.com/confirm/abc-123"
  }'
```

---

## 2. Confirmed Status Notification

**Endpoint**: `POST /api/notifications/ecosuite-confirmed-status/`

**When to Send**: When a reservation is confirmed (by customer or staff)

**Key Message**: Reservation confirmed, ready to welcome you

### Required Fields
- `email` - Customer email
- `customerName` - Customer name

### Optional Fields
- `reservationId`, `reservationDateTime`, `numberOfGuests`, `outletName`, `brandName`, `outletAddress`, `tableNumber`, `notes`

### Example Request
```bash
curl -X POST https://api.example.com/notifications/ecosuite-confirmed-status/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "customerName": "John Doe",
    "reservationId": "abc-123",
    "reservationDateTime": "2025-11-20T19:00:00+07:00",
    "numberOfGuests": 4,
    "outletName": "Grand Palace",
    "brandName": "Fine Dining Co.",
    "outletAddress": "123 Main St, City",
    "tableNumber": "15",
    "notes": "Window seat preferred"
  }'
```

### Email Features
- ✅ Green "CONFIRMED" badge
- 🎉 "We're Ready for You!" highlight box
- ⏰ Reminder to arrive on time
- Optional table number and address
- Professional green gradient header

---

## 3. Cancelled Notification

**Endpoint**: `POST /api/notifications/ecosuite-cancelled-notification/`

**When to Send**: When a reservation is cancelled (by customer or restaurant)

**Key Message**: Reservation cancelled, option to rebook

### Required Fields
- `email` - Customer email
- `customerName` - Customer name

### Optional Fields
- `reservationId`, `reservationDateTime`, `numberOfGuests`, `outletName`, `brandName`, `cancellationReason`, `cancelledBy`, `newBookingLink`

### Special Field: `cancelledBy`
- `"customer"` - Customer initiated cancellation (friendly tone)
- `"restaurant"` - Restaurant cancelled (apologetic tone)

### Example Request
```bash
curl -X POST https://api.example.com/notifications/ecosuite-cancelled-notification/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "customerName": "John Doe",
    "reservationId": "abc-123",
    "reservationDateTime": "2025-11-20T19:00:00+07:00",
    "numberOfGuests": 4,
    "outletName": "Grand Palace",
    "brandName": "Fine Dining Co.",
    "cancellationReason": "Schedule conflict",
    "cancelledBy": "customer",
    "newBookingLink": "https://example.com/book"
  }'
```

### Email Features
- ❌ Red "CANCELLED" badge
- Different message tone based on who cancelled
- 📅 "Book Again" call-to-action
- Optional cancellation reason
- Professional red/pink gradient header

---

## Complete Reservation Flow with Notifications

```
┌─────────────────────────────────────┐
│ 1. Customer Requests Reservation    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Staff Places Reservation         │
│    Status: "on hold"                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 📧 Send: ecosuite-on-hold-          │
│    notification                      │
│    "Booking received!"               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. [2 days before booking]          │
│    Customer confirms via link       │
│    Status: "confirmed"              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 📧 Send: ecosuite-confirmed-status  │
│    "Reservation confirmed!"         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Customer visits restaurant       │
└─────────────────────────────────────┘


Alternative Flow (Cancellation):
┌─────────────────────────────────────┐
│ Customer/Restaurant cancels         │
│ Status: "cancelled"                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 📧 Send: ecosuite-cancelled-        │
│    notification                      │
│    "Reservation cancelled"          │
└─────────────────────────────────────┘
```

---

## Integration Examples

### Python Integration (Django)

```python
import requests
from django.conf import settings

def send_reservation_notification(reservation, status):
    """
    Send appropriate notification based on reservation status
    """
    base_url = settings.BASE_URL
    customer_email = get_customer_email(reservation)
    
    if not customer_email:
        return False
    
    # Base payload
    payload = {
        'email': customer_email,
        'customerName': reservation['customerName'],
        'reservationId': reservation['id'],
        'reservationDateTime': reservation['reservationDateTime'],
        'numberOfGuests': reservation['numberOfGuests'],
        'outletName': get_outlet_name(reservation['outletId']),
        'brandName': get_brand_name(reservation['brandId']),
        'notes': reservation.get('notes')
    }
    
    # Determine which notification to send
    if status == 'on hold':
        endpoint = f"{base_url}/api/notifications/ecosuite-on-hold-notification/"
        payload['confirmationLink'] = f"{base_url}/api/ecosuite/confirm-reservation/{reservation['id']}/"
        
    elif status == 'confirmed':
        endpoint = f"{base_url}/api/notifications/ecosuite-confirmed-status/"
        payload['tableNumber'] = reservation.get('tableNumber')
        payload['outletAddress'] = get_outlet_address(reservation['outletId'])
        
    elif status == 'cancelled':
        endpoint = f"{base_url}/api/notifications/ecosuite-cancelled-notification/"
        payload['cancelledBy'] = reservation.get('cancelledBy', 'customer')
        payload['cancellationReason'] = reservation.get('cancellationReason')
        payload['newBookingLink'] = f"{base_url}/api/ecosuite/request-reservation/"
    else:
        return False
    
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send notification: {e}")
        return False
```

### JavaScript/Node.js Integration

```javascript
async function sendReservationNotification(reservation, status) {
  const baseUrl = process.env.BASE_URL;
  const customerEmail = await getCustomerEmail(reservation);
  
  if (!customerEmail) return false;
  
  // Base payload
  const payload = {
    email: customerEmail,
    customerName: reservation.customerName,
    reservationId: reservation.id,
    reservationDateTime: reservation.reservationDateTime,
    numberOfGuests: reservation.numberOfGuests,
    outletName: await getOutletName(reservation.outletId),
    brandName: await getBrandName(reservation.brandId),
    notes: reservation.notes
  };
  
  let endpoint;
  
  // Determine which notification to send
  switch(status) {
    case 'on hold':
      endpoint = `${baseUrl}/api/notifications/ecosuite-on-hold-notification/`;
      payload.confirmationLink = `${baseUrl}/api/ecosuite/confirm-reservation/${reservation.id}/`;
      break;
      
    case 'confirmed':
      endpoint = `${baseUrl}/api/notifications/ecosuite-confirmed-status/`;
      payload.tableNumber = reservation.tableNumber;
      payload.outletAddress = await getOutletAddress(reservation.outletId);
      break;
      
    case 'cancelled':
      endpoint = `${baseUrl}/api/notifications/ecosuite-cancelled-notification/`;
      payload.cancelledBy = reservation.cancelledBy || 'customer';
      payload.cancellationReason = reservation.cancellationReason;
      payload.newBookingLink = `${baseUrl}/api/ecosuite/request-reservation/`;
      break;
      
    default:
      return false;
  }
  
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return response.ok;
  } catch (error) {
    console.error('Failed to send notification:', error);
    return false;
  }
}
```

---

## All Response Formats

### Success Response (200 OK)
```json
{
  "status": "success",
  "email": "customer@example.com"
}
```

### Error Responses

**Missing Required Fields (400)**
```json
{
  "error": "Missing required fields: email and customerName"
}
```

**Invalid JSON (400)**
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

**Email Send Failure (500)**
```json
{
  "error": "SMTP connection failed"
}
```

---

## Email Design System

### Color Themes

| Status | Header Gradient | Badge Color | Accent Color |
|--------|----------------|-------------|--------------|
| On Hold | Purple (#667eea → #764ba2) | Yellow (#ffc107) | Purple (#667eea) |
| Confirmed | Green (#10b981 → #059669) | Green (#d4edda) | Green (#10b981) |
| Cancelled | Red/Pink (#f093fb → #f5576c) | Red (#f8d7da) | Red (#dc3545) |

### Common Design Elements

All emails include:
- Responsive design (mobile-friendly)
- Large emoji headers
- Status badges
- Detailed reservation info boxes
- Special highlight/action sections
- Professional footer
- Plain text fallback

---

## Testing All Notifications

### Test Script (bash)

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/notifications"
EMAIL="test@example.com"
DATETIME="2025-12-25T19:00:00+07:00"

# Test On Hold Notification
echo "Testing On Hold Notification..."
curl -X POST "${BASE_URL}/ecosuite-on-hold-notification/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${EMAIL}\",
    \"customerName\": \"Test User\",
    \"reservationId\": \"test-123\",
    \"reservationDateTime\": \"${DATETIME}\",
    \"numberOfGuests\": 4,
    \"outletName\": \"Test Restaurant\",
    \"brandName\": \"Test Brand\"
  }"

echo -e "\n\nTesting Confirmed Status..."
curl -X POST "${BASE_URL}/ecosuite-confirmed-status/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${EMAIL}\",
    \"customerName\": \"Test User\",
    \"reservationId\": \"test-123\",
    \"reservationDateTime\": \"${DATETIME}\",
    \"numberOfGuests\": 4,
    \"outletName\": \"Test Restaurant\",
    \"brandName\": \"Test Brand\",
    \"tableNumber\": \"15\"
  }"

echo -e "\n\nTesting Cancelled Notification..."
curl -X POST "${BASE_URL}/ecosuite-cancelled-notification/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${EMAIL}\",
    \"customerName\": \"Test User\",
    \"reservationId\": \"test-123\",
    \"reservationDateTime\": \"${DATETIME}\",
    \"numberOfGuests\": 4,
    \"outletName\": \"Test Restaurant\",
    \"brandName\": \"Test Brand\",
    \"cancelledBy\": \"customer\"
  }"
```

---

## Best Practices

### 1. When to Send Each Notification

| Notification | Trigger | Timing |
|--------------|---------|--------|
| On Hold | Reservation placed on hold by staff | Immediately after status change |
| Confirmed | Customer confirms or staff confirms | Immediately after confirmation |
| Cancelled | Reservation cancelled | Immediately after cancellation |

### 2. Email Content Tips

- **Always include** reservation ID, date/time, guests, outlet name
- **Include brand name** for multi-brand operations
- **Add confirmation/booking links** when relevant
- **Provide table numbers** when confirmed
- **Include address** in confirmed emails
- **Explain cancellation reasons** when available

### 3. Error Handling

```python
def safe_send_notification(reservation, status):
    try:
        result = send_reservation_notification(reservation, status)
        if not result:
            # Log failure but don't block reservation process
            logger.warning(f"Failed to send {status} notification for {reservation['id']}")
        return result
    except Exception as e:
        # Never let notification failure break reservation workflow
        logger.error(f"Notification error: {e}")
        return False
```

### 4. Rate Limiting

- Implement rate limiting if sending many emails
- Use background tasks/queues for high volume
- Monitor email service quotas

### 5. Testing

- Test with real email addresses
- Check spam filters
- Test on multiple email clients
- Verify mobile responsiveness

---

## Customization

### Change Brand Colors

Edit the notification functions in `notifications/views.py`:

```python
# On Hold - Purple theme
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);

# Confirmed - Green theme  
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);

# Cancelled - Red/Pink theme
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Add Company Logo

Add to each notification's HTML:

```python
<div class="header">
    <img src="https://your-cdn.com/logo.png" alt="Logo" style="max-width: 150px; margin-bottom: 10px;">
    <div class="header-icon">✅</div>
    <h1>Reservation Confirmed!</h1>
</div>
```

---

## Troubleshooting

### Emails Not Sending

1. Check Django email configuration in `settings.py`
2. Verify SMTP credentials
3. Check email service quotas
4. Review server logs for errors

### HTML Not Rendering

- Some email clients strip CSS
- Plain text version is automatically included
- Test with major clients (Gmail, Outlook, Apple Mail)

### Wrong Notification Sent

- Verify status values match exactly
- Check integration code logic
- Review notification selection conditions

---

## Related Documentation

- `ECOSUITE_ON_HOLD_NOTIFICATION.md` - Detailed on-hold docs
- `TWO_STEP_RESERVATION_FLOW.md` - Reservation workflow
- `RESERVATION_CONFIRMATION_ENDPOINT.md` - Confirmation page
- `RESERVATION_API_QUICK_REFERENCE.md` - API reference

---

## Summary Table

| Notification | Icon | Theme | When | Key Feature |
|--------------|------|-------|------|-------------|
| On Hold | 🎉 | Purple | Placed on hold | 2-day reminder message |
| Confirmed | ✅ | Green | Confirmed | Table number, address |
| Cancelled | ❌ | Red | Cancelled | Rebook button, custom message |

All notifications include professional design, mobile responsiveness, and comprehensive reservation details!





