"""
PythonAnywhere WSGI Configuration for TaraTech API
Copy this content to your PythonAnywhere WSGI configuration file
"""

import os
import sys

# Add your project directory to the Python path
path = '/home/taratechid/taratech_api'
if path not in sys.path:
    sys.path.append(path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'taratechapi.settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Alternative configuration if the above doesn't work:
# import os
# import sys
# 
# # Add the project directory to the Python path
# project_home = '/home/taratechid/taratech_api'
# if project_home not in sys.path:
#     sys.path.insert(0, project_home)
# 
# # Set environment variable
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taratechapi.settings')
# 
# # Import and create WSGI application
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application() 