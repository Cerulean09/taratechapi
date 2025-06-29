# PythonAnywhere Deployment Guide

## 🚨 **Current Issue: Unhandled Exception**

Your Django app is throwing an "Unhandled Exception" error on PythonAnywhere. Here's how to fix it:

## 🔧 **Step-by-Step Fix**

### 1. **Check PythonAnywhere Console**

1. Go to your PythonAnywhere dashboard
2. Click on "Consoles" → "Bash"
3. Navigate to your project directory:
   ```bash
   cd ~/taratech_api
   ```

### 2. **Check Python Version**

Make sure you're using the correct Python version:
```bash
python --version
python3 --version
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Run Django Checks**

```bash
python manage.py check
python manage.py collectstatic --noinput
```

### 5. **Test the App Locally**

```bash
python manage.py runserver 0.0.0.0:8000
```

### 6. **Check Error Logs**

In PythonAnywhere dashboard:
1. Go to "Web" tab
2. Click on your web app
3. Check "Error log" for specific error messages

## 🧪 **Test Your Deployment**

After uploading the updated files, test these endpoints:

### **Basic Test:**
```
https://taratechid.pythonanywhere.com/test/
```

### **Health Check:**
```
https://taratechid.pythonanywhere.com/health/
```

### **API Test:**
```
https://taratechid.pythonanywhere.com/api/
```

## 🔍 **Common Issues & Solutions**

### **Issue 1: Import Errors**
**Error:** `ModuleNotFoundError: No module named 'nocan'`

**Solution:**
1. Make sure your project structure is correct
2. Check that `nocan` is in `INSTALLED_APPS`
3. Restart your web app in PythonAnywhere

### **Issue 2: Template Errors**
**Error:** `TemplateDoesNotExist`

**Solution:**
- The updated code now handles missing templates gracefully
- It will return JSON responses instead of crashing

### **Issue 3: Database Errors**
**Error:** `Database connection issues`

**Solution:**
```bash
python manage.py migrate
```

### **Issue 4: Static Files**
**Error:** `Static files not found`

**Solution:**
```bash
python manage.py collectstatic --noinput
```

## 📁 **File Structure Check**

Make sure your PythonAnywhere file structure looks like this:

```
taratech_api/
├── manage.py
├── requirements.txt
├── taratechapi/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── nocan/
    ├── __init__.py
    ├── views.py
    ├── urls.py
    ├── apiViews.py
    ├── paymentApiViews.py
    ├── paymentService.py
    └── urlConfig.py
```

## 🚀 **PythonAnywhere Web App Configuration**

1. **Go to "Web" tab in PythonAnywhere**
2. **Source code:** `/home/yourusername/taratech_api`
3. **Working directory:** `/home/yourusername/taratech_api`
4. **WSGI configuration file:** Edit and make sure it points to:
   ```python
   import os
   import sys
   
   path = '/home/yourusername/taratech_api'
   if path not in sys.path:
       sys.path.append(path)
   
   os.environ['DJANGO_SETTINGS_MODULE'] = 'taratechapi.settings'
   
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

## 🔄 **Restart Your Web App**

After making changes:
1. Go to "Web" tab
2. Click "Reload" button
3. Wait for the green checkmark

## 🧪 **Testing Commands**

### **Local Testing:**
```bash
python check_config.py
python test_payment_api.py
```

### **Online Testing:**
```bash
curl https://taratechid.pythonanywhere.com/health/
curl https://taratechid.pythonanywhere.com/test/
```

## 📞 **If Still Not Working**

1. **Check PythonAnywhere error logs**
2. **Run the health check endpoint**
3. **Check the test endpoint**
4. **Verify all files are uploaded correctly**

## 🎯 **Expected Results**

After fixing, you should see:

- **Health Check:** `{"status": "healthy", "message": "All modules loaded successfully"}`
- **Test Endpoint:** `{"message": "TaraTech API is working!", "status": "success"}`
- **API Endpoint:** JSON response with API information

## 🔧 **Debug Mode**

The settings are temporarily set to `DEBUG = True` to help you see error details. Once everything is working, you can set it back to `False` for production. 