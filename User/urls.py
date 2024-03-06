from django.urls import path
from .views import user_registration, user_login  ,check_email , check_identifient

from . import views

urlpatterns = [
    path('register/', user_registration, name='user-registration'),
    path('login/', user_login, name='user-login'),
    path('check_identifient/<str:cin>/', views.check_identifient, name='check_identifient'),
    path('inactive_users/', views.inactive_users, name='inactive_users'),
    path('validate_user_account/<str:cin>/', views.validate_user_account, name='validate_user_account'),
    path('check_email/', views.check_email, name='check_email'),
    path('send_Email/', views.send_Email, name='send_Email'),
    path('check_cin/', views.check_cin, name='check_cin'),
    path('start-session/', views.start_session, name='start_session'),
    path('check-session/', views.check_session, name='check_session'),
    path('end-session/', views.end_session, name='end_session'),
    #reset password
    path('demande_reset_password/<str:cin>/', views.demande_reset_password, name='demande_reset_password'),
    path('reset_password_users/', views.reset_password_users, name='reset_password_users'),
    path('reset_password/<str:cin>/', views.reset_password, name='reset_password'),
]
