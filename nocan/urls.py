from django.urls import path
from . import views
from . import apiViews
from . import paymentApiViews

urlpatterns = [
    path('', views.myapp),
    path('api/', views.api),
    path('api/docs/', views.apiDocumentation, name='apiDocumentation'),
    
    # Supabase API endpoints
    path('api/supabase/test-connection/', apiViews.testConnection, name='testConnection'),
    path('api/supabase/get-data/', apiViews.getData, name='getData'),
    path('api/supabase/insert-data/', apiViews.insertData, name='insertData'),
    path('api/supabase/update-data/', apiViews.updateData, name='updateData'),
    path('api/supabase/delete-data/', apiViews.deleteData, name='deleteData'),
    path('api/supabase/execute-query/', apiViews.executeQuery, name='executeQuery'),
    path('api/supabase/table-info/', apiViews.getTableInfo, name='getTableInfo'),
    path('api/supabase/auth/login/', apiViews.authenticateUser, name='authenticateUser'),
    path('api/supabase/auth/register/', apiViews.registerUser, name='registerUser'),
    
    # Payment API endpoints
    path('api/payment/create/', paymentApiViews.createPayment, name='createPayment'),
    path('api/payment/<str:paymentId>/status/', paymentApiViews.getPaymentStatus, name='getPaymentStatus'),
    path('api/payment/<str:paymentId>/simulate/', paymentApiViews.simulatePayment, name='simulatePayment'),
]