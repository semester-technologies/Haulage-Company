from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name="register-user"),
    path('login/', login_view, name="login-user"),
    path('logout/', logout_view, name="logout-user"),
    # path('dashboard/', dashboard, name="dashboard"),
    # path('profile/', user_profile, name="user-profile"),
    # path('update-profile/', update_profile, name="update-profile"),

    # path('reset-password/', password_reset_request, name='password_reset_request'),
    # path('reset-password/<int:user_id>/', password_reset_confirm, name='password_reset_confirm'),

    path('companies/', company_list, name='company_list'),
    path('companies/create/', company_create, name='company_create'),
    path('companies/<int:company_id>/delete/', company_delete, name='company_delete'),
    path('companies/<int:company_id>/employees/', employee_list, name='employee_list'),
    path('companies/<int:company_id>/employees/create/', employee_create, name='employee_create'),
    path('employees/<int:employee_id>/delete/', employee_delete, name='employee_delete'),

    
]