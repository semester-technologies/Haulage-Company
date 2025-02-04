from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_user, name="register-user"),
    path('login/', login_user, name="login-user"),
    path('logout/', logout_user, name="logout-user"),
    path('dashboard/', dashboard, name="dashboard"),
    path('profile/', user_profile, name="user-profile"),
    path('update-profile/', update_profile, name="update-profile"),

    
    path('referrals/', referral_list, name='referral-list'),
    path('pending-approvals/', pending_approvals, name='pending-approvals'),
    path('referrals/<int:user_id>/', referral_detail, name='referral-detail'),
    path('referrals/<int:user_id>/approve/', approve_referral, name='approve-referral'),
    path('referrals/<int:user_id>/reject/', reject_referral, name='reject-referral'),

    path('submit-kyc/', submit_kyc, name='submit-kyc'),

    path('reset-password/', password_reset_request, name='password_reset_request'),
    path('reset-password/<int:user_id>/', password_reset_confirm, name='password_reset_confirm'),
    
]