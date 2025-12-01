# Two-Step Reservation Flow

## Overview
The reservation system now uses a two-step flow to handle conflicts gracefully:
1. **Check Availability** - Check if the requested time has conflicts
2. **Create Reservation** - Create the reservation based on user's choice

This allows users to make an informed decision about joining the waitlist or choosing another time.

## The Two Endpoints

### 1. Check Reservation Availability (Step 1)

**Endpoint**: `GET /ecosuite/check-reservation-availability/`

**Purpose**: Check if a time slot is available without creating a reservation.

**Required Parameters**:
- `brandId` - Brand ID
- `outletId` - Outlet ID  
- `dateTime` - Reservation date/time (ISO format)

**Optional Parameters**:
- `guests` - Number of guests (for future capacity checks)

**Example Request**:
```
GET /api/ecosuite/check-reservation-availability/?brandId=ABC123&outletId=XYZ789&dateTime=2025-11-20T19:00:00+07:00
```

**Response - Available** (200 OK):
```json
{
  "available": true,
  "hasConflicts": false,
  "requestedDateTime": "2025-11-20T19:00:00+07:00",
  "recommendedStatus": "pending",
  "conflictingReservations": 0,
  "message": "Reservations available for this time slot",
  "suggestedAction": null
}
```

**Response - Conflicts Exist** (200 OK):
```json
{
  "available": false,
  "hasConflicts": true,
  "requestedDateTime": "2025-11-20T19:00:00+07:00",
  "recommendedStatus": "waitlisted",
  "conflictingReservations": 2,
  "message": "There are existing reservations within 2 hours of your requested time. You can join the waitlist or choose another time.",
  "suggestedAction": "join_waitlist_or_choose_another_time"
}
```

### 2. Request Reservation (Step 2)

**Endpoint**: `GET /ecosuite/request-reservation/`

**Purpose**: Create a reservation after checking availability.

**Required Parameters**:
- `name` - Customer name
- `phone` - International phone number
- `guests` - Number of guests
- `dateTime` - Reservation date/time (ISO format)
- `brandId` - Brand ID
- `outletId` - Outlet ID

**Conditional Parameters**:
- `joinWaitlist` - "true" or "false" (REQUIRED if conflicts exist)

**Optional Parameters**:
- `notes` - Additional notes

**Example Requests**:

**No Conflicts - Create Pending Reservation**:
```
GET /api/ecosuite/request-reservation/?name=John+Doe&phone=+6281234567890&guests=4&dateTime=2025-11-20T19:00:00+07:00&brandId=ABC123&outletId=XYZ789
```

**With Conflicts - Join Waitlist**:
```
GET /api/ecosuite/request-reservation/?name=John+Doe&phone=+6281234567890&guests=4&dateTime=2025-11-20T19:00:00+07:00&brandId=ABC123&outletId=XYZ789&joinWaitlist=true
```

**With Conflicts - Decline Waitlist**:
```
GET /api/ecosuite/request-reservation/?name=John+Doe&phone=+6281234567890&guests=4&dateTime=2025-11-20T19:00:00+07:00&brandId=ABC123&outletId=XYZ789&joinWaitlist=false
```

**Responses**:

**Success - No Conflicts** (201 Created):
```json
{
  "message": "Reservation request created successfully",
  "reservation": {
    "id": "abc-123-def",
    "status": "pending",
    "customerName": "John Doe",
    "customerPhone": "+6281234567890",
    "numberOfGuests": 4,
    "reservationDateTime": "2025-11-20T19:00:00+07:00",
    ...
  }
}
```

**Success - Joined Waitlist** (201 Created):
```json
{
  "message": "Reservation request created successfully",
  "reservation": {
    "id": "abc-123-def",
    "status": "waitlisted",
    "customerName": "John Doe",
    ...
  }
}
```

**Error - Conflicts Without Decision** (409 Conflict):
```json
{
  "error": "Conflict detected",
  "message": "There are existing reservations within 2 hours of your requested time. Please choose an action.",
  "hasConflicts": true,
  "requestedDateTime": "2025-11-20T19:00:00+07:00",
  "actions": {
    "joinWaitlist": "Add '&joinWaitlist=true' to join the waitlist",
    "chooseAnotherTime": "Add '&joinWaitlist=false' or select a different time"
  },
  "suggestedAction": "Please use the check-reservation-availability endpoint first to see availability"
}
```

**Error - Declined Waitlist** (400 Bad Request):
```json
{
  "error": "Reservation not created",
  "message": "You chose not to join the waitlist. Please select a different time for your reservation.",
  "hasConflicts": true,
  "requestedDateTime": "2025-11-20T19:00:00+07:00",
  "suggestion": "Use the check-reservation-availability endpoint to find available times"
}
```

## Complete Flow Examples

### Flow 1: Available Time (No Conflicts)

**Step 1: Check Availability**
```bash
curl "https://api.example.com/ecosuite/check-reservation-availability/?brandId=ABC123&outletId=XYZ789&dateTime=2025-11-20T19:00:00+07:00"
```

Response: `available: true, hasConflicts: false`

**Step 2: Create Reservation** (no joinWaitlist needed)
```bash
curl "https://api.example.com/ecosuite/request-reservation/?name=John+Doe&phone=+6281234567890&guests=4&dateTime=2025-11-20T19:00:00+07:00&brandId=ABC123&outletId=XYZ789"
```

Result: Reservation created with status `"pending"`

### Flow 2: Conflict - User Joins Waitlist

**Step 1: Check Availability**
```bash
curl "https://api.example.com/ecosuite/check-reservation-availability/?brandId=ABC123&outletId=XYZ789&dateTime=2025-11-20T19:00:00+07:00"
```

Response: `available: false, hasConflicts: true, suggestedAction: "join_waitlist_or_choose_another_time"`

**Step 2: User Decides to Join Waitlist**
```bash
curl "https://api.example.com/ecosuite/request-reservation/?name=John+Doe&phone=+6281234567890&guests=4&dateTime=2025-11-20T19:00:00+07:00&brandId=ABC123&outletId=XYZ789&joinWaitlist=true"
```

Result: Reservation created with status `"waitlisted"`

### Flow 3: Conflict - User Chooses Another Time

**Step 1: Check Availability**
```bash
curl "https://api.example.com/ecosuite/check-reservation-availability/?brandId=ABC123&outletId=XYZ789&dateTime=2025-11-20T19:00:00+07:00"
```

Response: `available: false, hasConflicts: true`

**Step 2: User Declines Waitlist** (or tries different times)
```bash
curl "https://api.example.com/ecosuite/check-reservation-availability/?brandId=ABC123&outletId=XYZ789&dateTime=2025-11-20T21:00:00+07:00"
```

Response: `available: true, hasConflicts: false`

**Step 3: Create Reservation at New Time**
```bash
curl "https://api.example.com/ecosuite/request-reservation/?name=John+Doe&phone=+6281234567890&guests=4&dateTime=2025-11-20T21:00:00+07:00&brandId=ABC123&outletId=XYZ789"
```

Result: Reservation created with status `"pending"`

### Flow 4: Direct Creation Without Checking (Error Case)

**Attempt to Create with Conflicts**
```bash
curl "https://api.example.com/ecosuite/request-reservation/?name=John+Doe&phone=+6281234567890&guests=4&dateTime=2025-11-20T19:00:00+07:00&brandId=ABC123&outletId=XYZ789"
```

Response: `409 Conflict` - Must specify `joinWaitlist=true` or `joinWaitlist=false`

## User Interface Flow

### Recommended UI Implementation

```
┌─────────────────────────────────────┐
│  1. User fills reservation form     │
│     - Name, Phone, Guests, DateTime │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  2. Call check-reservation-         │
│     availability API                │
└─────────────┬───────────────────────┘
              │
              ├──► Available
              │    │
              │    ▼
              │   ┌─────────────────────────────┐
              │   │ Show "Available" message    │
              │   │ [Confirm Reservation] btn   │
              │   └──────────┬──────────────────┘
              │              │
              │              ▼
              │   ┌─────────────────────────────┐
              │   │ Call request-reservation    │
              │   │ (no joinWaitlist param)     │
              │   │ → Status: "pending"         │
              │   └─────────────────────────────┘
              │
              └──► Conflicts Detected
                   │
                   ▼
                  ┌──────────────────────────────────┐
                  │ Show conflict message            │
                  │ "There are X reservations..."    │
                  │                                  │
                  │ [Join Waitlist] [Choose Another] │
                  └──────────┬──────────┬────────────┘
                             │          │
                   Join ◄────┘          └────► Another Time
                   Waitlist                    │
                     │                         ▼
                     ▼                    ┌────────────────┐
        ┌─────────────────────────┐     │ Show date/time │
        │ Call request-reservation│     │ picker again   │
        │ with joinWaitlist=true  │     │ → Repeat flow  │
        │ → Status: "waitlisted"  │     └────────────────┘
        └─────────────────────────┘
```

## Frontend Implementation Examples

### JavaScript/React Example

```javascript
async function createReservation(formData) {
  // Step 1: Check availability
  const checkUrl = new URL('https://api.example.com/ecosuite/check-reservation-availability/');
  checkUrl.searchParams.append('brandId', formData.brandId);
  checkUrl.searchParams.append('outletId', formData.outletId);
  checkUrl.searchParams.append('dateTime', formData.dateTime);
  
  const checkResponse = await fetch(checkUrl);
  const availability = await checkResponse.json();
  
  if (availability.available) {
    // No conflicts - create directly
    return await createReservationDirect(formData);
  } else {
    // Conflicts exist - ask user
    const userChoice = await showConflictDialog(availability);
    
    if (userChoice === 'waitlist') {
      return await createReservationDirect(formData, true);
    } else if (userChoice === 'another-time') {
      // Show date picker again
      return showDatePicker();
    }
  }
}

async function createReservationDirect(formData, joinWaitlist = null) {
  const url = new URL('https://api.example.com/ecosuite/request-reservation/');
  url.searchParams.append('name', formData.name);
  url.searchParams.append('phone', formData.phone);
  url.searchParams.append('guests', formData.guests);
  url.searchParams.append('dateTime', formData.dateTime);
  url.searchParams.append('brandId', formData.brandId);
  url.searchParams.append('outletId', formData.outletId);
  
  if (joinWaitlist !== null) {
    url.searchParams.append('joinWaitlist', joinWaitlist.toString());
  }
  
  const response = await fetch(url);
  return await response.json();
}

function showConflictDialog(availability) {
  return new Promise((resolve) => {
    // Show modal with conflict message
    const modal = `
      <div class="modal">
        <h3>Time Slot Conflict</h3>
        <p>${availability.message}</p>
        <p>There are ${availability.conflictingReservations} reservations near your requested time.</p>
        <button onclick="resolve('waitlist')">Join Waitlist</button>
        <button onclick="resolve('another-time')">Choose Another Time</button>
      </div>
    `;
    // Show modal and resolve based on user choice
  });
}
```

### HTML Form Example

```html
<form id="reservationForm">
  <input type="text" name="name" required placeholder="Your Name">
  <input type="tel" name="phone" required placeholder="+6281234567890">
  <input type="number" name="guests" required placeholder="Number of Guests">
  <input type="datetime-local" name="dateTime" required>
  <input type="hidden" name="brandId" value="ABC123">
  <input type="hidden" name="outletId" value="XYZ789">
  <button type="submit">Check Availability</button>
</form>

<div id="conflictDialog" style="display:none;">
  <p id="conflictMessage"></p>
  <button onclick="joinWaitlist()">Join Waitlist</button>
  <button onclick="chooseAnotherTime()">Choose Another Time</button>
</div>

<script>
document.getElementById('reservationForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  
  // Check availability first
  const params = new URLSearchParams(formData);
  const checkUrl = `/api/ecosuite/check-reservation-availability/?${params}`;
  const checkResp = await fetch(checkUrl);
  const availability = await checkResp.json();
  
  if (availability.available) {
    // Create reservation directly
    createReservation(formData);
  } else {
    // Show conflict dialog
    document.getElementById('conflictMessage').textContent = availability.message;
    document.getElementById('conflictDialog').style.display = 'block';
  }
});

async function joinWaitlist() {
  const formData = new FormData(document.getElementById('reservationForm'));
  formData.append('joinWaitlist', 'true');
  await createReservation(formData);
}

function chooseAnotherTime() {
  document.getElementById('conflictDialog').style.display = 'none';
  // User can modify the datetime input
}

async function createReservation(formData) {
  const params = new URLSearchParams(formData);
  const url = `/api/ecosuite/request-reservation/?${params}`;
  const response = await fetch(url);
  const result = await response.json();
  
  if (response.ok) {
    alert(`Reservation created! Status: ${result.reservation.status}`);
  } else {
    alert(`Error: ${result.message}`);
  }
}
</script>
```

## Benefits of Two-Step Flow

1. **User Control** - Users make informed decisions about waitlist
2. **Better UX** - Clear communication about conflicts
3. **Flexibility** - Users can easily try different times
4. **Transparent** - Shows how many conflicts exist
5. **Prevents Surprises** - No automatic waitlisting without user consent
6. **API Separation** - Check and create are independent operations

## Status Flow Chart

```
User Request
     │
     ▼
Check Availability
     │
     ├──► No Conflicts ──► Create ──► status: "pending"
     │
     └──► Has Conflicts
             │
             ├──► joinWaitlist=true ──► Create ──► status: "waitlisted"
             │
             └──► joinWaitlist=false ──► Error ──► Choose another time
```

## Error Handling

### Missing joinWaitlist Parameter
If conflicts exist but no `joinWaitlist` parameter is provided:
- Returns `409 Conflict`
- Includes helpful message about what to do
- Suggests using check-availability endpoint first

### Invalid joinWaitlist Value
If `joinWaitlist` is not "true" or "false":
- Returns `400 Bad Request`
- Indicates valid values

### Declining Waitlist
If user sets `joinWaitlist=false` with conflicts:
- Returns `400 Bad Request`
- Suggests checking other times
- No reservation is created

## Best Practices

1. **Always Check First** - Use check-availability before showing reservation form
2. **Cache Check Results** - Store availability check for a few minutes
3. **Show Alternative Times** - If conflicts exist, suggest nearby available slots
4. **Clear Messaging** - Make it obvious when user is joining waitlist
5. **Confirmation** - Send different confirmations for pending vs waitlisted
6. **Staff Notification** - Alert staff about waitlisted reservations

## Migration Notes

Existing integrations should:
1. Add check-availability call before request-reservation
2. Handle 409 Conflict responses
3. Implement UI for waitlist decision
4. Update documentation for users
5. Consider backward compatibility if needed





