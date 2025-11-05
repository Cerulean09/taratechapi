from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='ecosuite_index'),
    path('hello/', views.hello, name='ecosuite_hello'),
    path('register/', views.register),
    path('login/', views.login_user),
    path('logout/', views.logout_user),
    path('profile/', views.profile),

]
