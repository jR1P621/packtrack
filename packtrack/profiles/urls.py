from django.urls import path
from . import views

urlpatterns = [
    # path('register', views.view_register, name='register'),
    path('', views.view_hashers, name='hashers'),
    path('<str:username>', views.view_profile, name='profile'),
    path('<str:username>/edit', views.edit_profile, name='edit_profile'),
]