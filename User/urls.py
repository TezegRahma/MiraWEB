from django.urls import path
from .views import user_registration, user_login , user_detail ,check_email , check_identifient

from . import views

urlpatterns = [
    path('register/', user_registration, name='user-registration'),
    path('login/', user_login, name='user-login'),
    path('detail/<int:cin>/', user_detail, name='user-detail'),
    path('check-email/', views.check_email, name='check_email'),
    path('check-identifient/', views.check_identifient, name='check_identifient'),


]
