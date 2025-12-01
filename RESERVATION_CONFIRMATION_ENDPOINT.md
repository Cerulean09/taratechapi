# Reservation Confirmation Endpoint

## Overview
This endpoint allows customers to confirm or cancel their reservation through a beautiful, user-friendly web interface. The link can be sent via email, SMS, WhatsApp, or any messaging service.

## Endpoint
```
GET/POST /ecosuite/confirm-reservation/<reservation_id>/
```

## Features
- ✅ **Beautiful UI** - Modern, responsive design that works on all devices
- ✅ **No authentication required** - Customers can access directly via link
- ✅ **Two actions** - Confirm or Cancel reservation
- ✅ **Instant feedback** - Shows success/error pages after action
- ✅ **Mobile-friendly** - Optimized for mobile devices
- ✅ **Automatic updates** - Directly updates the reservation status in Supabase

## How It Works

### 1. Display Confirmation Page (GET without action)
When a customer visits the link without taking action, they see a beautiful confirmation page with:
- Reservation details (name, phone, guests, date/time, status, notes)
- Two action buttons: "Confirm Booking" and "Cancel Booking"
- Confirmation dialogs before taking action

### 2. Process Action (POST or GET with action parameter)
When the customer clicks a button:
- **Confirm** - Updates reservation status to `"confirmed"`
- **Cancel** - Updates reservation status to `"cancelled"`
- Shows a success page with updated reservation details

## Usage Examples

### Basic Confirmation Link
Send this link to your customer via email or messaging:

```
https://your-domain.com/api/ecosuite/confirm-reservation/550e8400-e29b-41d4-a716-446655440002/
```

### Direct Action Links (Optional)
You can also create direct action links:

**Confirm directly:**
```
https://your-domain.com/api/ecosuite/confirm-reservation/550e8400-e29b-41d4-a716-446655440002/?action=confirm
```

**Cancel directly:**
```
https://your-domain.com/api/ecosuite/confirm-reservation/550e8400-e29b-41d4-a716-446655440002/?action=cancel
```

### Integration with Messaging Services

#### Email Template Example
```html
<p>Hello {{ customer_name }},</p>
<p>Your reservation has been received!</p>
<p>Please click the link below to confirm your booking:</p>
<a href="https://your-domain.com/api/ecosuite/confirm-reservation/{{ reservation_id }}/">
  Confirm My Reservation
</a>
```

#### WhatsApp Message Example
```
Hi {{ customer_name }}! 

Your reservation for {{ number_of_guests }} guests on {{ date_time }} has been received.

Please confirm your booking here:
https://your-domain.com/api/ecosuite/confirm-reservation/{{ reservation_id }}/

Thank you!
```

#### SMS Example
```
Reservation confirmed for {{ date_time }}. Click to confirm: https://your-domain.com/api/ecosuite/confirm-reservation/{{ reservation_id }}/
```

## UI Screenshots Description

### Confirmation Page
The initial page displays:
- 🎉 Celebration emoji and welcoming header
- Card with reservation details:
  - Customer name
  - Phone number
  - Number of guests
  - Date and time (formatted: "Monday, November 20, 2025 at 07:00 PM")
  - Current status badge
  - Notes (if any)
- Two large, accessible buttons:
  - "✓ Confirm Booking" (purple gradient)
  - "✗ Cancel Booking" (gray)

### Success Page (Confirmed)
- ✅ Large checkmark icon with animation
- "Reservation Confirmed!" heading
- Success message
- Summary of confirmed reservation
- Notice about confirmation email

### Success Page (Cancelled)
- ❌ Cancel icon with animation
- "Reservation Cancelled" heading
- Cancellation message
- Summary of cancelled reservation
- Notice about making new reservations

### Error Page
- ⚠️ Warning icon
- Error title and message
- Clean, friendly design

## Status Updates

| Current Status | After Confirm | After Cancel |
|----------------|---------------|--------------|
| pending | confirmed | cancelled |
| waitlisted | confirmed | cancelled |
| requested | confirmed | cancelled |
| confirmed | confirmed | cancelled |
| cancelled | confirmed | cancelled |

**Note:** The action will work regardless of current status, allowing flexibility in workflow.

## API Response Behavior

### GET without action parameter
- **Returns**: HTML page with confirmation UI
- **Status Code**: 200 OK
- **Content-Type**: text/html

### POST or GET with action parameter
- **Returns**: HTML page with success or error message
- **Status Code**: 200 OK (even for errors, as HTML is returned)
- **Content-Type**: text/html
- **Database**: Reservation status updated in Supabase

## Example Workflow

### Step 1: Customer Makes Reservation
```
Customer visits: /api/ecosuite/request-reservation/?name=John&phone=+1234567890&...
Reservation created with status: "pending" or "waitlisted"
```

### Step 2: System Sends Confirmation Link
```
System generates link: /api/ecosuite/confirm-reservation/abc-123-def/
Link sent via email/SMS/WhatsApp
```

### Step 3: Customer Opens Link
```
Customer sees beautiful confirmation page
Reviews reservation details
```

### Step 4: Customer Takes Action
```
Customer clicks "Confirm Booking"
Status updated to "confirmed" in database
Customer sees success page
```

## Integration Code Examples

### Python - Send Email with Confirmation Link
```python
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_confirmation_email(reservation):
    confirmation_link = f"https://your-domain.com/api/ecosuite/confirm-reservation/{reservation['id']}/"
    
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>Confirm Your Reservation</h2>
        <p>Hello {reservation['customerName']},</p>
        <p>Your reservation details:</p>
        <ul>
          <li>Date & Time: {reservation['reservationDateTime']}</li>
          <li>Guests: {reservation['numberOfGuests']}</li>
          <li>Status: {reservation['status']}</li>
        </ul>
        <p>
          <a href="{confirmation_link}" 
             style="background-color: #667eea; color: white; padding: 12px 24px; 
                    text-decoration: none; border-radius: 8px; display: inline-block;">
            Confirm My Reservation
          </a>
        </p>
      </body>
    </html>
    """
    
    # Send email using your email service
    # ... email sending code ...
```

### JavaScript - Generate Confirmation Link
```javascript
function generateConfirmationLink(reservationId) {
  const baseUrl = 'https://your-domain.com';
  return `${baseUrl}/api/ecosuite/confirm-reservation/${reservationId}/`;
}

function sendWhatsAppMessage(phoneNumber, reservation) {
  const confirmLink = generateConfirmationLink(reservation.id);
  const message = `Hi ${reservation.customerName}! 
  
Your reservation for ${reservation.numberOfGuests} guests on ${reservation.reservationDateTime} has been received.

Please confirm your booking here:
${confirmLink}

Thank you!`;
  
  // Send via WhatsApp API
  // ... WhatsApp API code ...
}
```

### cURL - Testing the Endpoint
```bash
# View confirmation page
curl https://your-domain.com/api/ecosuite/confirm-reservation/abc-123-def/

# Confirm reservation
curl -X POST \
  -d "action=confirm" \
  https://your-domain.com/api/ecosuite/confirm-reservation/abc-123-def/

# Cancel reservation
curl -X POST \
  -d "action=cancel" \
  https://your-domain.com/api/ecosuite/confirm-reservation/abc-123-def/
```

## Security Considerations

1. **UUID-based Links**: Reservation IDs are UUIDs, making them hard to guess
2. **No Authentication Required**: Intentional for ease of use, but consider:
   - Rate limiting to prevent abuse
   - Logging all confirmation/cancellation actions
   - Email/SMS verification before sending links
3. **Idempotent Actions**: Confirming or canceling multiple times is safe
4. **Status Validation**: Consider checking current status before allowing actions

## Best Practices

### 1. Send Links Promptly
- Send confirmation link immediately after reservation is created
- Include deadline for confirmation if needed

### 2. Include Context
- Always include reservation details in the message
- Make it clear what the customer is confirming

### 3. Track Actions
- Monitor confirmation rates
- Send reminders if not confirmed within timeframe
- Consider automatic cancellation for unconfirmed reservations

### 4. Handle Edge Cases
- Expired reservations: Check date before allowing confirmation
- Already confirmed: Show appropriate message
- Invalid IDs: Error page is already handled

### 5. Follow-up Actions
- Send confirmation email after customer confirms
- Notify staff about confirmed reservations
- Add to calendar/reminder systems

## Customization

The HTML templates are now proper Django templates located in `ecosuite/templates/ecosuite/`:

- `base.html` - Base template with common styling
- `confirm_reservation.html` - Initial confirmation page
- `reservation_success.html` - Success page (for both confirm/cancel)
- `reservation_error.html` - Error pages

### How to Customize

1. **Edit Templates Directly**: Modify the HTML files in the templates directory
2. **Change Colors**: Update the CSS in each template's `{% block extra_styles %}`
3. **Add Branding**: Add logos or custom elements in the templates
4. **Modify Layout**: Change the structure within `{% block content %}`

### Example: Adding a Logo
Edit `base.html`:
```html
<div class="container">
    <img src="/static/img/logo.png" alt="Your Brand" class="logo">
    {% block content %}{% endblock %}
</div>
```

### Example: Changing Button Colors
Edit `confirm_reservation.html`:
```css
.btn-confirm {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
}
```

See `ecosuite/templates/ecosuite/README.md` for detailed customization guide.

## Troubleshooting

### Link doesn't work
- Verify the reservation ID is correct
- Check that the reservation exists in the database
- Ensure the URL structure matches the endpoint

### Action doesn't update database
- Check Supabase connection
- Verify table permissions
- Look at server logs for errors

### UI doesn't display correctly
- Clear browser cache
- Check mobile responsiveness
- Verify HTML is rendering properly

## Next Steps

After implementing this endpoint:
1. ✅ Create email templates with confirmation links
2. ✅ Set up SMS/WhatsApp integration
3. ✅ Add logging for confirmation actions
4. ✅ Implement reminder system for unconfirmed reservations
5. ✅ Create admin dashboard to monitor confirmations
6. ✅ Add analytics to track confirmation rates

