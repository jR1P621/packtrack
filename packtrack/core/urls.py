from django.urls import path
from . import views

urlpatterns = [
    # path('register/', CreateUserView.as_view(), name='register')
    # path('register', views.view_register, name='register'),
    path('', views.view_dashboard, name='dashboard'),
]