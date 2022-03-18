from django.urls import path
from . import views
from profiles.views import edit_profile

urlpatterns = [
    # path('register/', CreateUserView.as_view(), name='register')
    # path('register', views.view_register, name='register'),
    path('', views.view_dashboard, name='dashboard'),
    path('edit_profile', edit_profile, name='edit_profile'),
]