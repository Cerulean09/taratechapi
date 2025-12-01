# Reservation API Quick Reference

## Endpoints Overview

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/ecosuite/check-reservation-availability/` | GET | None | Check if time slot is available |
| `/ecosuite/request-reservation/` | GET | None | Create a new reservation request |
| `/ecosuite/confirm-reservation/<id>/` | GET/POST | None | Confirm or cancel reservation via UI |
| `/ecosuite/get-reservations/` | GET | Required | List all reservations (filtered) |
| `/ecosuite/upsert-reservation/<id>/` | POST/PUT/PATCH | Required | Create/update reservation (admin) |

## Quick Usage

### 1. Check Availability (Step 1)
```bash
GET /ecosuite/check-reservation-availability/?brandId=ABC&outletId=XYZ&dateTime=2025-11-20T19:00:00+07:00
```
**Response:**
```json
{
  "available": true/false,
  "hasConflicts": true/false,
  "message": "...",
  "conflictingReservations": 0,
  "suggestedAction": "join_waitlist_or_choose_another_time" or null
}
```

### 2. Create Reservation (Step 2)

**If No Conflicts:**
```bash
GET /ecosuite/request-reservation/?name=John&phone=+6281234567890&guests=4&dateTime=2025-11-20T19:00:00+07:00&brandId=ABC&outletId=XYZ
```

**If Conflicts - Join Waitlist:**
```bash
GET /ecosuite/request-reservation/?name=John&phone=+6281234567890&guests=4&dateTime=2025-11-20T19:00:00+07:00&brandId=ABC&outletId=XYZ&joinWaitlist=true
```

**If Conflicts - Choose Another Time:**
```bash
# Check different time
GET /ecosuite/check-reservation-availability/?brandId=ABC&outletId=XYZ&dateTime=2025-11-20T21:00:00+07:00
```

### 3. Send Confirmation Link
```
https://your-domain.com/api/ecosuite/confirm-reservation/<reservation-id>/
```

## Status Values

| Status | Meaning | How It's Set |
|--------|---------|--------------|
| `pending` | No conflicts, awaiting confirmation | Automatic (no conflicts) |
| `waitlisted` | Has conflicts, user joined waitlist | User choice (joinWaitlist=true) |
| `confirmed` | User confirmed the reservation | User action via link |
| `cancelled` | User cancelled the reservation | User action via link |
| `on hold` | Reserved by staff (blocks others) | Staff action |

## Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success (check-availability) | Process result |
| 201 | Reservation created | Success! |
| 400 | Bad request / Invalid params | Check parameters |
| 409 | Conflict - need user decision | Ask user: waitlist or another time |

## Complete Flow Diagram

```
                Start
                  │
                  ▼
    ┌─────────────────────────┐
    │ User fills form         │
    │ (name, phone, guests,   │
    │  dateTime, etc.)        │
    └────────────┬────────────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │ Call:                   │
    │ check-reservation-      │
    │ availability            │
    └────────┬────────────────┘
             │
    ┌────────┴────────┐
    │                 │
 Available      Has Conflicts
    │                 │
    │                 ▼
    │    ┌────────────────────────┐
    │    │ Show dialog:           │
    │    │ • Join Waitlist        │
    │    │ • Choose Another Time  │
    │    └─────┬──────────┬───────┘
    │          │          │
    │    Join  │          │ Another
    │   Waitlist         Time
    │          │          │
    │          │          ▼
    │          │    (Back to form)
    │          │
    ├──────────┤
    │          │
    ▼          ▼
┌──────────────────────┐
│ Call:                │
│ request-reservation  │
│ (with joinWaitlist   │
│  param if needed)    │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Reservation Created  │
│ Status: "pending"    │
│     or "waitlisted"  │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Send confirmation    │
│ link to customer     │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Customer clicks link │
│ Confirms or cancels  │
└──────────────────────┘
```

## Common Patterns

### Pattern 1: Simple Reservation (No Conflicts)
```javascript
// 1. Check
const check = await fetch('/check-reservation-availability/?...');
if (check.available) {
  // 2. Create
  const reservation = await fetch('/request-reservation/?...');
  // 3. Send confirmation
  sendEmail(reservation.id);
}
```

### Pattern 2: Handle Conflicts
```javascript
// 1. Check
const check = await fetch('/check-reservation-availability/?...');
if (check.hasConflicts) {
  // 2. Ask user
  const choice = await askUser("Join waitlist or choose another time?");
  if (choice === 'waitlist') {
    // 3. Create with waitlist
    await fetch('/request-reservation/?...&joinWaitlist=true');
  } else {
    // 3. Show time picker again
    showTimePicker();
  }
}
```

### Pattern 3: Multiple Time Attempts
```javascript
const times = ['19:00', '19:30', '20:00', '20:30'];
for (const time of times) {
  const check = await fetch(`/check-reservation-availability/?...&dateTime=${time}`);
  if (check.available) {
    // Show this as available option
    showAvailableTime(time);
  }
}
```

## Query Parameter Encoding

Remember to URL encode parameters:

| Character | Encoded | Example |
|-----------|---------|---------|
| Space | `%20` or `+` | `John Doe` → `John+Doe` |
| + | `%2B` | `+62812` → `%2B62812` |
| : | `%3A` | `19:00` → `19%3A00` (but usually not needed in values) |

**Full encoded example:**
```
/request-reservation/?name=John+Doe&phone=%2B6281234567890&dateTime=2025-11-20T19:00:00%2B07:00&...
```

## Testing Checklist

- [ ] Check availability with no conflicts
- [ ] Check availability with conflicts
- [ ] Create reservation when available
- [ ] Create reservation with waitlist choice
- [ ] Try to create without joinWaitlist parameter (should get 409)
- [ ] Set joinWaitlist=false with conflicts (should get 400)
- [ ] Confirm reservation via link
- [ ] Cancel reservation via link
- [ ] Test with invalid reservation ID (error page)
- [ ] Test phone number normalization (+, space, etc.)
- [ ] Test datetime normalization (+ in timezone)

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 409 Conflict | Conflicts exist, no joinWaitlist | Add `&joinWaitlist=true` or `false` |
| 400 on waitlist=false | User declined, has conflicts | Check other times |
| Phone format error | Missing + or wrong format | Use international format: +6281234567890 |
| DateTime format error | Wrong format or encoding | Use ISO: 2025-11-20T19:00:00+07:00 |
| Template not found | Django template missing | Check templates/ecosuite/ directory |

## Tips

1. **Always check first** - Call check-availability before showing form confirmation
2. **Cache intelligently** - Cache availability checks for 1-2 minutes
3. **Show alternatives** - If conflicts, show nearby available times
4. **Clear communication** - Make waitlist vs pending clear to users
5. **Mobile friendly** - Confirmation pages work on all devices
6. **Error handling** - Handle all response codes appropriately

## Status Workflow

```
requested → (deprecated, not used in new flow)
pending   → confirmed / cancelled (user action)
waitlisted → confirmed / cancelled (user action)
on hold   → (staff managed, blocks others)
confirmed → (final state)
cancelled → (final state)
```

## For Developers

**Key Files:**
- `/ecosuite/views.py` - Main logic
- `/ecosuite/urls.py` - Endpoint definitions  
- `/ecosuite/templates/ecosuite/*.html` - UI templates
- `TWO_STEP_RESERVATION_FLOW.md` - Detailed flow documentation

**Helper Functions:**
- `check_reservation_conflicts()` - Checks for conflicts
- `format_reservation_datetime()` - Formats datetime for display
- `create_supabase_client()` - Supabase connection

## Support

For detailed documentation:
- Two-step flow: `TWO_STEP_RESERVATION_FLOW.md`
- Confirmation page: `RESERVATION_CONFIRMATION_ENDPOINT.md`
- Request endpoint: `RESERVATION_REQUEST_ENDPOINT.md`
- Django templates: `DJANGO_TEMPLATES_SUMMARY.md`





