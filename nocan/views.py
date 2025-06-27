from django.shortcuts import render

# Create your views here.
# request handler

def myapp(request):
    return render(request, 'main.html', {'title': 'Hello World'})

def api(request):
    return render(request, 'api.html', {'title': 'API'})

def apiDocumentation(request):
    return render(request, 'api_documentation.html', {'title': 'Supabase API Documentation'})