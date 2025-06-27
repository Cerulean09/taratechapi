# Tara Tech Ops Web - Supabase API

A Django-based API that provides a comprehensive interface for interacting with Supabase databases. This API handles CRUD operations, authentication, and data management for Supabase projects.

## Features

- 🔐 **Authentication**: User registration and login with Supabase Auth
- 📊 **Database Operations**: Full CRUD operations (Create, Read, Update, Delete)
- 🔍 **Query Execution**: Custom SQL query execution
- 📋 **Table Information**: Get database schema information
- 🛡️ **Security**: CSRF protection, input validation, and error handling
- 📚 **Documentation**: Comprehensive API documentation
- 🧪 **Testing**: Built-in test suite for API endpoints

## Prerequisites

- Python 3.8+
- Django 5.2+
- Supabase account and project
- Virtual environment (recommended)

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd taratech_api
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

## Configuration

### Supabase Setup

1. **Create a Supabase project**:
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Note your project URL and API keys

2. **Configure environment variables**:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_ANON_KEY`: Your Supabase anonymous key

3. **Set up database tables** (example):
   ```sql
   -- Example users table
   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       email VARCHAR(255) UNIQUE NOT NULL,
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```

## API Endpoints

### Base URL
All API endpoints are prefixed with: `/api/supabase/`

### Authentication
- `POST /api/supabase/auth/register/` - Register new user
- `POST /api/supabase/auth/login/` - Authenticate user

### Database Operations
- `GET /api/supabase/test-connection/` - Test Supabase connection
- `GET /api/supabase/get-data/` - Retrieve data from table
- `POST /api/supabase/insert-data/` - Insert new data
- `PUT /api/supabase/update-data/` - Update existing data
- `DELETE /api/supabase/delete-data/` - Delete data
- `POST /api/supabase/execute-query/` - Execute custom SQL
- `GET /api/supabase/table-info/` - Get table information

### Documentation
- `GET /api/docs/` - API documentation page

## Usage Examples

### JavaScript/Fetch API

```javascript
// Test connection
fetch('/api/supabase/test-connection/')
    .then(response => response.json())
    .then(data => console.log(data));

// Get data from a table
fetch('/api/supabase/get-data/?table=users&limit=10')
    .then(response => response.json())
    .then(data => console.log(data));

// Insert new data
fetch('/api/supabase/insert-data/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        table: 'users',
        data: {
            name: 'John Doe',
            email: 'john@example.com'
        }
    })
})
.then(response => response.json())
.then(data => console.log(data));

// Update data
fetch('/api/supabase/update-data/', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        table: 'users',
        data: { name: 'Jane Doe' },
        conditions: { id: 1 }
    })
})
.then(response => response.json())
.then(data => console.log(data));

// Delete data
fetch('/api/supabase/delete-data/', {
    method: 'DELETE',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        table: 'users',
        conditions: { id: 1 }
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python/Requests

```python
import requests
import json

# Test connection
response = requests.get('http://localhost:8000/api/supabase/test-connection/')
print(response.json())

# Get data
response = requests.get('http://localhost:8000/api/supabase/get-data/?table=users&limit=5')
print(response.json())

# Insert data
data = {
    "table": "users",
    "data": {
        "name": "John Doe",
        "email": "john@example.com"
    }
}
response = requests.post(
    'http://localhost:8000/api/supabase/insert-data/',
    json=data,
    headers={'Content-Type': 'application/json'}
)
print(response.json())
```

## Testing

Run the test suite to verify API functionality:

```bash
python test_supabase_api.py
```

Or test individual endpoints:

```bash
# Test connection
curl http://localhost:8000/api/supabase/test-connection/

# Get data
curl "http://localhost:8000/api/supabase/get-data/?table=users&limit=5"

# Insert data
curl -X POST http://localhost:8000/api/supabase/insert-data/ \
  -H "Content-Type: application/json" \
  -d '{"table": "users", "data": {"name": "Test User", "email": "test@example.com"}}'
```

## Response Format

All API endpoints return responses in a standardized format:

```json
{
    "success": true/false,
    "message": "Description of the operation result",
    "data": {
        // Response data or null if error
    }
}
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid parameters or missing required fields
- **401 Unauthorized**: Authentication failed
- **500 Internal Server Error**: Database or server error

## Security Considerations

- ✅ CSRF protection enabled
- ✅ Input validation and sanitization
- ✅ Environment variable configuration
- ✅ Error logging and monitoring
- ✅ HTTPS recommended for production

## Development

### Project Structure
```
taratech_api/
├── nocan/
│   ├── __init__.py
│   ├── views.py              # Main views
│   ├── apiViews.py           # API endpoints
│   ├── supabaseClient.py     # Supabase client configuration
│   ├── urls.py               # URL routing
│   └── templates/
│       └── api_documentation.html
├── taratechapi/
│   ├── settings.py           # Django settings
│   └── urls.py               # Main URL configuration
├── test_supabase_api.py      # Test suite
└── README.md                 # This file
```

### Adding New Endpoints

1. Add the view function to `nocan/apiViews.py`
2. Add the URL pattern to `nocan/urls.py`
3. Update the documentation in `nocan/templates/api_documentation.html`
4. Add tests to `test_supabase_api.py`

## Deployment

### Production Setup

1. **Set environment variables**:
   ```bash
   export SUPABASE_URL=https://your-project.supabase.co
   export SUPABASE_ANON_KEY=your-anon-key-here
   export DEBUG=False
   export SECRET_KEY=your-secret-key
   ```

2. **Configure web server** (e.g., Nginx + Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn taratechapi.wsgi:application
   ```

3. **Set up SSL/HTTPS** for production

4. **Configure logging** for production monitoring

## Troubleshooting

### Common Issues

1. **Connection Error**: Check Supabase URL and API key
2. **Table Not Found**: Verify table exists in Supabase
3. **Authentication Failed**: Check user credentials
4. **CORS Issues**: Configure CORS settings for frontend

### Debug Mode

Enable debug mode for detailed error messages:
```python
# In settings.py
DEBUG = True
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Check the API documentation at `/api/docs/`
- Review the test suite for usage examples
- Open an issue on GitHub

---

**Note**: This API is designed to work with Supabase. Make sure you have a valid Supabase project configured before using the API endpoints. 