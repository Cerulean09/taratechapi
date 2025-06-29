from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
# request handler

def myapp(request):
    try:
        return render(request, 'main.html', {'title': 'Hello World'})
    except Exception as e:
        # If template doesn't exist, return a simple response
        return JsonResponse({
            'message': 'TaraTech API is running!',
            'status': 'success',
            'error': str(e) if DEBUG else 'Template error'
        })

def api(request):
    try:
        return render(request, 'api.html', {'title': 'API'})
    except Exception as e:
        # If template doesn't exist, return API info
        return JsonResponse({
            'message': 'TaraTech API Endpoints',
            'endpoints': {
                'base_url': 'https://taratechid.pythonanywhere.com/api',
                'payment': 'https://taratechid.pythonanywhere.com/api/payment',
                'supabase': 'https://taratechid.pythonanywhere.com/api/supabase'
            },
            'status': 'success',
            'error': str(e) if DEBUG else 'Template error'
        })

def apiDocumentation(request):
    try:
        return render(request, 'api_documentation.html', {'title': 'Supabase API Documentation'})
    except Exception as e:
        # If template doesn't exist, return documentation info
        return JsonResponse({
            'message': 'API Documentation',
            'documentation_url': 'https://taratechid.pythonanywhere.com/PAYMENT_API_README.md',
            'status': 'success',
            'error': str(e) if DEBUG else 'Template error'
        })

@csrf_exempt
def test_view(request):
    """Simple test view to verify the app is working"""
    return JsonResponse({
        'message': 'TaraTech API is working!',
        'status': 'success',
        'timestamp': '2024-01-01T12:00:00Z'
    })

@csrf_exempt
def health_check(request):
    """Health check endpoint for PythonAnywhere"""
    try:
        # Test imports
        from . import apiViews
        from . import paymentApiViews
        from . import urlConfig
        
        return JsonResponse({
            'status': 'healthy',
            'message': 'All modules loaded successfully',
            'environment': 'production',
            'base_url': 'https://taratechid.pythonanywhere.com'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Module import error: {str(e)}',
            'environment': 'production'
        }, status=500)