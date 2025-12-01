# Reservation Request Endpoint

## Overview
This endpoint allows anyone to create a reservation request from anywhere (website, Instagram, social media, etc.) by simply accessing a URL with query parameters. No authentication is required.

## Endpoint
```
GET /ecosuite/request-reservation/
```

## Features
- **No authentication required** - accessible from anywhere
- **Intelligent status determination** - automatically checks for conflicts and sets status:
  - **"waitlisted"** - if there are "on hold" reservations within 2 hours before or after the requested time
  - **"pending"** - if no conflicts exist
- **Simple GET request** - can be used as a clickable link
- **Conflict detection** - prevents double-booking by checking existing reservations

## Required Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `name` | string | Customer name | `John Doe` |
| `phone` | string | International phone number | `+6281234567890` |
| `guests` | integer | Number of guests | `4` |
| `dateTime` | string | Reservation date and time (ISO format) | `2025-11-20T19:00:00Z` |
| `brandId` | string | Brand ID (UUID) | `550e8400-e29b-41d4-a716-446655440000` |
| `outletId` | string | Outlet ID (UUID) | `550e8400-e29b-41d4-a716-446655440001` |

## Optional Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `notes` | string | Additional notes | `Window seat preferred` |

## Example Usage

### Basic Link (Recommended - with URL encoding)
```
https://your-domain.com/ecosuite/request-reservation/?name=John%20Doe&phone=%2B6281234567890&guests=4&dateTime=2025-11-20T19:00:00%2B07:00&brandId=550e8400-e29b-41d4-a716-446655440000&outletId=550e8400-e29b-41d4-a716-446655440001
```

### Basic Link (Also works - without encoding +)
```
https://your-domain.com/ecosuite/request-reservation/?name=John%20Doe&phone=+6281234567890&guests=4&dateTime=2025-11-20T19:00:00+07:00&brandId=550e8400-e29b-41d4-a716-446655440000&outletId=550e8400-e29b-41d4-a716-446655440001
```

### Phone Number Formats (All Accepted)
The endpoint accepts and normalizes various phone number formats:
- `phone=+6281234567890` → `+6281234567890` ✅
- `phone=%2B6281234567890` → `+6281234567890` ✅
- `phone=6281234567890` → `+6281234567890` ✅ (automatically adds +)
- `phone= 6281234567890` → `+6281234567890` ✅ (space from decoded + is fixed)

### With Notes
```
https://your-domain.com/ecosuite/request-reservation/?name=John%20Doe&phone=%2B6281234567890&guests=4&dateTime=2025-11-20T19:00:00Z&brandId=550e8400-e29b-41d4-a716-446655440000&outletId=550e8400-e29b-41d4-a716-446655440001&notes=Window%20seat%20preferred
```

### Using cURL
```bash
curl -X GET "https://your-domain.com/ecosuite/request-reservation/?name=John%20Doe&phone=%2B6281234567890&guests=4&dateTime=2025-11-20T19:00:00Z&brandId=550e8400-e29b-41d4-a716-446655440000&outletId=550e8400-e29b-41d4-a716-446655440001"
```

### Using JavaScript
```javascript
const reservationUrl = new URL('https://your-domain.com/ecosuite/request-reservation/');
reservationUrl.searchParams.append('name', 'John Doe');
reservationUrl.searchParams.append('phone', '+6281234567890');
reservationUrl.searchParams.append('guests', '4');
reservationUrl.searchParams.append('dateTime', '2025-11-20T19:00:00Z');
reservationUrl.searchParams.append('brandId', '550e8400-e29b-41d4-a716-446655440000');
reservationUrl.searchParams.append('outletId', '550e8400-e29b-41d4-a716-446655440001');
reservationUrl.searchParams.append('notes', 'Window seat preferred');

fetch(reservationUrl)
  .then(response => response.json())
  .then(data => console.log(data));
```

## Response

### Success Response (201 Created) - No Conflicts
```json
{
  "message": "Reservation request created successfully",
  "reservation": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "brandId": "550e8400-e29b-41d4-a716-446655440000",
    "outletId": "550e8400-e29b-41d4-a716-446655440001",
    "customerName": "John Doe",
    "customerPhone": "+6281234567890",
    "numberOfGuests": 4,
    "reservationDateTime": "2025-11-20T19:00:00+07:00",
    "status": "pending",
    "notes": "Window seat preferred",
    "createdAt": "2025-11-17T10:30:00.000Z",
    "updatedAt": "2025-11-17T10:30:00.000Z",
    "payments": [],
    "tableId": null,
    "checkedInAt": null,
    "checkedInBy": null,
    "checkedOutAt": null,
    "checkedOutBy": null,
    "createdBy": null,
    "updatedBy": null
  }
}
```

### Success Response (201 Created) - With Conflicts
When there are "on hold" reservations within 2 hours of the requested time:
```json
{
  "message": "Reservation request created successfully",
  "reservation": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "brandId": "550e8400-e29b-41d4-a716-446655440000",
    "outletId": "550e8400-e29b-41d4-a716-446655440001",
    "customerName": "John Doe",
    "customerPhone": "+6281234567890",
    "numberOfGuests": 4,
    "reservationDateTime": "2025-11-20T19:00:00+07:00",
    "status": "waitlisted",
    "notes": "Window seat preferred",
    "createdAt": "2025-11-17T10:30:00.000Z",
    "updatedAt": "2025-11-17T10:30:00.000Z",
    "payments": [],
    "tableId": null,
    "checkedInAt": null,
    "checkedInBy": null,
    "checkedOutAt": null,
    "checkedOutBy": null,
    "createdBy": null,
    "updatedBy": null
  }
}
```

### Error Response (400 Bad Request)
```json
{
  "error": "Customer name is required",
  "parameter": "name"
}
```

## Use Cases

### 1. Instagram Bio Link
Add this link to your Instagram bio to allow customers to request reservations directly:
```
https://your-domain.com/ecosuite/request-reservation/?brandId=YOUR_BRAND_ID&outletId=YOUR_OUTLET_ID
```
Note: Customers will need to manually add other parameters or you can create a simple form page.

### 2. QR Code
Generate a QR code that points to a reservation request form page, which then constructs the URL with all parameters and redirects to this endpoint.

### 3. Website Integration
Embed a form on your website that collects the required information and constructs the URL to call this endpoint.

### 4. Social Media Posts
Share direct links in social media posts for special events or promotions.

## Important Notes

1. **Automatic Status Determination**: The status is automatically determined based on reservation conflicts:
   - **"waitlisted"** - Assigned when there are existing "on hold" reservations within 2 hours (before or after) of the requested time at the same outlet
   - **"pending"** - Assigned when no conflicting reservations are found
   - This helps manage capacity and prevents overbooking

2. **Phone Number Format**: Phone numbers should be in international format (e.g., +6281234567890). The endpoint automatically handles URL decoding, so both `+6281234567890` and `%2B6281234567890` work correctly. If no `+` is provided, it will be automatically added.

3. **Date/Time Format**: Use ISO 8601 format for dates (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DDTHH:MM:SS+HH:MM). The endpoint automatically handles the URL decoding issue where `+` in timezone becomes a space.

4. **URL Encoding**: Remember to URL encode special characters in the query string (spaces become %20, + becomes %2B, etc.). **Note**: The endpoint now automatically fixes both phone numbers and timezone offsets, so you don't need to worry about encoding the `+` sign - both `+` and `%2B` will work correctly.

5. **No Authentication**: This endpoint does not require authentication, making it perfect for public-facing reservation requests.

6. **Auto-Generated ID**: The reservation ID is automatically generated as a UUID.

7. **Brand and Outlet IDs**: You need to know the brand ID and outlet ID beforehand. These can be obtained from the authenticated admin endpoints.

## Security Considerations

While this endpoint is public, consider:
- Implementing rate limiting to prevent abuse
- Adding CAPTCHA for web-based forms
- Monitoring for spam or malicious requests
- Validating phone numbers server-side
- Setting up notifications for new reservation requests

## How Conflict Detection Works

The endpoint automatically checks for reservation conflicts to help manage capacity:

1. **Time Window**: Checks for existing reservations within **2 hours before** and **2 hours after** the requested time
2. **Scope**: Only checks reservations at the same `brandId` and `outletId`
3. **Status Filter**: Only considers reservations with status **"on hold"**
4. **Result**:
   - If **any** "on hold" reservations are found in the 4-hour window → status = **"waitlisted"**
   - If **no** "on hold" reservations are found → status = **"pending"**

### Example Scenarios

**Scenario 1: No Conflicts**
- Requested time: `2025-11-20 19:00:00`
- Existing reservations: None with "on hold" status between 17:00 and 21:00
- **Result**: Status = `"pending"`

**Scenario 2: With Conflicts**
- Requested time: `2025-11-20 19:00:00`
- Existing reservation: `2025-11-20 18:30:00` with status "on hold"
- **Result**: Status = `"waitlisted"` (within 2-hour window)

**Scenario 3: Outside Time Window**
- Requested time: `2025-11-20 19:00:00`
- Existing reservation: `2025-11-20 16:30:00` with status "on hold"
- **Result**: Status = `"pending"` (more than 2 hours before)

## Next Steps After Reservation Request

Once a reservation is created:
1. **If status is "pending"**: Ready to be confirmed by staff
2. **If status is "waitlisted"**: Staff should review capacity and either:
   - Confirm if space is available
   - Contact customer about alternative times
3. Staff can view reservations in the admin panel
4. Status can be updated using the authenticated `upsert-reservation` endpoint
5. Tables can be assigned to confirmed reservations

