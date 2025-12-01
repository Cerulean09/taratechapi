# Ecosuite HTML Templates

This directory contains Django HTML templates for the reservation confirmation system.

## Template Structure

### Base Template
- **base.html** - Base template with common styling and structure
  - Provides responsive layout
  - Includes common CSS styles
  - Defines blocks for content customization

### Confirmation Templates

#### 1. confirm_reservation.html
Main confirmation page where customers can review and take action on their reservation.

**Context Variables:**
- `reservation` - Reservation object with all details
- `formatted_datetime` - Formatted date/time string

**Features:**
- Displays all reservation details
- Two action buttons (Confirm/Cancel)
- Confirmation dialogs before actions
- Status badges with different colors
- Mobile responsive design

#### 2. reservation_success.html
Success page shown after confirming or cancelling a reservation.

**Context Variables:**
- `reservation` - Updated reservation object
- `formatted_datetime` - Formatted date/time string
- `action` - "confirmed" or "cancelled"

**Features:**
- Different styling based on action type
- Animated success/cancel icon
- Reservation summary
- Contextual message based on action

#### 3. reservation_error.html
Error page for various error scenarios.

**Context Variables:**
- `error_title` - Error title
- `error_message` - Error description

**Features:**
- Warning icon
- Clear error messaging
- Friendly design

## Customization

### Colors and Styling
All templates extend `base.html`. You can customize:
- Background gradients in each template's `{% block background %}`
- Additional styles in `{% block extra_styles %}`
- Layout structure in `{% block content %}`

### Example: Changing Confirm Button Color
Edit `confirm_reservation.html`:

```css
{% block extra_styles %}
...
.btn-confirm {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
    color: white;
}
...
{% endblock %}
```

### Example: Adding Logo
Edit `base.html` to add a logo to all pages:

```html
<div class="container">
    <img src="/static/your-logo.png" alt="Logo" class="logo">
    {% block content %}{% endblock %}
</div>
```

## Template Variables

### Reservation Object Fields
```python
{
    'id': 'uuid',
    'customerName': 'string',
    'customerPhone': 'string',
    'numberOfGuests': integer,
    'reservationDateTime': 'ISO datetime string',
    'status': 'string',  # pending, waitlisted, confirmed, cancelled
    'notes': 'string',
    'brandId': 'string',
    'outletId': 'string',
    'createdAt': 'ISO datetime string',
    'updatedAt': 'ISO datetime string'
}
```

## Adding New Templates

1. Create new HTML file in this directory
2. Extend base.html: `{% extends "ecosuite/base.html" %}`
3. Override blocks as needed
4. Update views.py to use the new template

## Django Template Filters Used

- `{{ variable|lower }}` - Convert to lowercase
- `{{ variable|title }}` - Convert to title case
- `{% if condition %}` - Conditional rendering
- `{% csrf_token %}` - CSRF protection for forms

## Mobile Responsive

All templates include media queries for mobile devices:
- Adjusts padding and font sizes
- Stacks buttons vertically on small screens
- Word wrapping for long content

## Browser Support

These templates support:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)





