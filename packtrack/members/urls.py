from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path('profile', views.view_profile, name='profile'),
    path('register', views.view_register, name='register'),
    path('', views.view_dashboard, name='dashboard')
]