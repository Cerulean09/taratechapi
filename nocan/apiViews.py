import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.gzip import gzip_page
from .supabaseClient import supabaseManager
import logging

logger = logging.getLogger(__name__)

def createApiResponse(success=True, data=None, message="", statusCode=200):
    """Create a standardized API response"""
    response = {
        "success": success,
        "message": message,
        "data": data
    }
    return JsonResponse(response, status=statusCode)

@csrf_exempt
@require_http_methods(["GET"])
def testConnection(request):
    """Test the connection to Supabase"""
    try:
        isConnected = supabaseManager.testConnection()
        if isConnected:
            return createApiResponse(True, {"connected": True}, "Supabase connection successful")
        else:
            return createApiResponse(False, {"connected": False}, "Supabase connection failed", 500)
    except Exception as e:
        logger.error(f"Connection test error: {str(e)}")
        return createApiResponse(False, None, f"Connection error: {str(e)}", 500)

@csrf_exempt
@require_http_methods(["GET"])
def getData(request):
    """Get data from a Supabase table"""
    try:
        tableName = request.GET.get('table')
        limit = request.GET.get('limit', 100)
        offset = request.GET.get('offset', 0)
        
        if not tableName:
            return createApiResponse(False, None, "Table name is required", 400)
        
        client = supabaseManager.getClient()
        query = client.table(tableName).select('*')
        
        # Apply limit and offset
        if limit:
            query = query.limit(int(limit))
        if offset:
            query = query.range(int(offset), int(offset) + int(limit) - 1)
        
        response = query.execute()
        
        return createApiResponse(True, response.data, f"Data retrieved from {tableName}")
        
    except Exception as e:
        logger.error(f"Get data error: {str(e)}")
        return createApiResponse(False, None, f"Error retrieving data: {str(e)}", 500)

@csrf_exempt
@require_http_methods(["POST"])
def insertData(request):
    """Insert data into a Supabase table"""
    try:
        body = json.loads(request.body)
        tableName = body.get('table')
        data = body.get('data')
        
        if not tableName or not data:
            return createApiResponse(False, None, "Table name and data are required", 400)
        
        client = supabaseManager.getClient()
        response = client.table(tableName).insert(data).execute()
        
        return createApiResponse(True, response.data, f"Data inserted into {tableName}")
        
    except json.JSONDecodeError:
        return createApiResponse(False, None, "Invalid JSON in request body", 400)
    except Exception as e:
        logger.error(f"Insert data error: {str(e)}")
        return createApiResponse(False, None, f"Error inserting data: {str(e)}", 500)

@csrf_exempt
@require_http_methods(["PUT"])
def updateData(request):
    """Update data in a Supabase table"""
    try:
        body = json.loads(request.body)
        tableName = body.get('table')
        data = body.get('data')
        conditions = body.get('conditions', {})
        
        if not tableName or not data:
            return createApiResponse(False, None, "Table name and data are required", 400)
        
        client = supabaseManager.getClient()
        query = client.table(tableName).update(data)
        
        # Apply conditions if provided
        for key, value in conditions.items():
            query = query.eq(key, value)
        
        response = query.execute()
        
        return createApiResponse(True, response.data, f"Data updated in {tableName}")
        
    except json.JSONDecodeError:
        return createApiResponse(False, None, "Invalid JSON in request body", 400)
    except Exception as e:
        logger.error(f"Update data error: {str(e)}")
        return createApiResponse(False, None, f"Error updating data: {str(e)}", 500)

@csrf_exempt
@require_http_methods(["DELETE"])
def deleteData(request):
    """Delete data from a Supabase table"""
    try:
        body = json.loads(request.body)
        tableName = body.get('table')
        conditions = body.get('conditions', {})
        
        if not tableName:
            return createApiResponse(False, None, "Table name is required", 400)
        
        client = supabaseManager.getClient()
        query = client.table(tableName).delete()
        
        # Apply conditions if provided
        for key, value in conditions.items():
            query = query.eq(key, value)
        
        response = query.execute()
        
        return createApiResponse(True, response.data, f"Data deleted from {tableName}")
        
    except json.JSONDecodeError:
        return createApiResponse(False, None, "Invalid JSON in request body", 400)
    except Exception as e:
        logger.error(f"Delete data error: {str(e)}")
        return createApiResponse(False, None, f"Error deleting data: {str(e)}", 500)

@csrf_exempt
@require_http_methods(["POST"])
def executeQuery(request):
    """Execute a custom SQL query"""
    try:
        body = json.loads(request.body)
        query = body.get('query')
        
        if not query:
            return createApiResponse(False, None, "SQL query is required", 400)
        
        client = supabaseManager.getClient()
        response = client.rpc('execute_sql', {'sql_query': query}).execute()
        
        return createApiResponse(True, response.data, "Query executed successfully")
        
    except json.JSONDecodeError:
        return createApiResponse(False, None, "Invalid JSON in request body", 400)
    except Exception as e:
        logger.error(f"Execute query error: {str(e)}")
        return createApiResponse(False, None, f"Error executing query: {str(e)}", 500)

@csrf_exempt
@require_http_methods(["GET"])
def getTableInfo(request):
    """Get information about tables in the database"""
    try:
        client = supabaseManager.getClient()
        
        # This is a simplified approach - you might need to adjust based on your Supabase setup
        response = client.rpc('get_table_info').execute()
        
        return createApiResponse(True, response.data, "Table information retrieved")
        
    except Exception as e:
        logger.error(f"Get table info error: {str(e)}")
        return createApiResponse(False, None, f"Error retrieving table info: {str(e)}", 500)

@csrf_exempt
@require_http_methods(["POST"])
def authenticateUser(request):
    """Authenticate a user with Supabase"""
    try:
        body = json.loads(request.body)
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return createApiResponse(False, None, "Email and password are required", 400)
        
        client = supabaseManager.getClient()
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        return createApiResponse(True, {
            "user": response.user,
            "session": response.session
        }, "User authenticated successfully")
        
    except json.JSONDecodeError:
        return createApiResponse(False, None, "Invalid JSON in request body", 400)
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return createApiResponse(False, None, f"Authentication failed: {str(e)}", 401)

@csrf_exempt
@require_http_methods(["POST"])
def registerUser(request):
    """Register a new user with Supabase"""
    try:
        body = json.loads(request.body)
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return createApiResponse(False, None, "Email and password are required", 400)
        
        client = supabaseManager.getClient()
        response = client.auth.sign_up({
            "email": email,
            "password": password
        })
        
        return createApiResponse(True, {
            "user": response.user,
            "session": response.session
        }, "User registered successfully")
        
    except json.JSONDecodeError:
        return createApiResponse(False, None, "Invalid JSON in request body", 400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return createApiResponse(False, None, f"Registration failed: {str(e)}", 400) 