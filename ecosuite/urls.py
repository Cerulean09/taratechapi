from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='ecosuite_index'),
    path('hello/', views.hello, name='ecosuite_hello'),
    path('register/', views.register),
    path('login/', views.login_user),
    path('logout/', views.logout_user),
    path('profile/', views.profile),
    path('get-all-users/', views.get_all_users, name='get_all_users'),
    path('update-user/<str:user_id>/', views.update_user, name='update_user'),
    
    # Brand Management Endpoints
    path('admin/brands/', views.get_all_brands, name='get_all_brands'),
    path('admin/brands/', views.create_brand, name='create_brand'),
    path('admin/brands/<str:brand_id>/', views.get_brand, name='get_brand'),
    path('admin/brands/<str:brand_id>/', views.update_brand, name='update_brand'),
    path('admin/brands/<str:brand_id>/suspend/', views.suspend_brand, name='suspend_brand'),
    path('brands/upsert/', views.upsert_brand, name='upsert_brand'),
    path('brands/<str:brand_id>/upload-logo/', views.upload_brand_logo, name='upload_brand_logo'),
]
