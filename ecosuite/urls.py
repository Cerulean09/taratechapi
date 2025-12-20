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
    path('get-all-brands/', views.get_all_brands, name='get_all_brands'),
    path('create-brand/', views.create_brand, name='create_brand'),
    path('get-brand/<str:brand_id>/', views.get_brand, name='get_brand'),
    path('update-brand/<str:brand_id>/', views.update_brand, name='update_brand'),
    path('suspend-brand/<str:brand_id>/', views.suspend_brand, name='suspend_brand'),
    path('upsert-brand/', views.upsert_brand, name='upsert_brand'),
    path('upload-brand-logo/<str:brand_id>/', views.upload_brand_logo, name='upload_brand_logo'),
    path('upload-brand-floor-image/<str:brand_id>/', views.upload_brand_floor_image, name='upload_brand_floor_image'),
    path('upload-outlet-floor-image/<str:outlet_id>/', views.upload_outlet_floor_image, name='upload_outlet_floor_image'),
    
    # Table Management Endpoints
    path('upsert-table/<str:table_id>/', views.upsert_table, name='upsert_table'),
    
    # Reservation Management Endpoints
    path('get-reservations/', views.get_reservations, name='get_reservations'),
    path('get-reservations-for-brand-with-reservation-id/<str:brand_id>/<str:reservation_id>/', views.get_reservations_for_brand_with_reservation_id, name='get_reservations_for_brand_with_reservation_id'),
    path('get-reservations-for-brand-with-phone-number/<str:brand_id>/<str:phone_number>/', views.get_reservations_for_brand_with_phone_number, name='get_reservations_for_brand_with_phone_number'),
    path('upsert-reservation/<str:reservation_id>/', views.upsert_reservation, name='upsert_reservation'),
    path('upsert-crm-customer/<str:customer_id>/', views.upsert_crm_customer, name='upsert_crm_customer'),
    path('get-crm-customers/', views.get_crm_customers, name='get_crm_customers'),
    path('check-reservation-availability/', views.check_reservation_availability, name='check_reservation_availability'),
    path('request-reservation/', views.request_reservation, name='request_reservation'),
    path('confirm-reservation/<str:reservation_id>/', views.confirm_reservation, name='confirm_reservation'),
    path('check-for-reservations-2-days-before-reservation-date/', views.check_for_reservations_2_days_before_reservation_date, name='check_for_reservations_2_days_before_reservation_date'),
    path('send-reservation-reminder-for-5pax-and-above-1day-before-reservation-date/', views.send_reservation_reminder_for_5pax_and_above_1day_before_reservation_date, name='send_reservation_reminder_for_5pax_and_above_1day_before_reservation_date'),

    # Pivot Integration
    path('pivot/create-payment/', views.pivot_create_payment, name='pivot_create_payment'),
    path('pivot/check-payment/<str:reservation_id>/', views.pivot_check_payment, name='pivot_check_payment'),
    path('pivot/check-all-pending-payments/', views.pivot_check_all_pending_payments, name='pivot_check_all_pending_payments'),
    # path('pivot/confirm-payment/', views.pivot_confirm_payment, name='pivot_confirm_payment'),
    # path('pivot/payment-method-configs/', views.pivot_payment_method_configs, name='pivot_payment_method_configs'),
]
