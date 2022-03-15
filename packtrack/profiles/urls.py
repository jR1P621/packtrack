from django.urls import path
from . import views

urlpatterns = [
    # path('register', views.view_register, name='register'),
    # path('hashers', views.view_hashers, name='hashers'),
    path('<str:username>', views.view_profile, name='profile'),
    # path('edit_profile', views.edit_profile, name='edit_profile'),
]