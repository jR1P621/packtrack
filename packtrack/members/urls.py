from django.urls import path
from . import views

urlpatterns = [
    path('register', views.view_register, name='register'),
    path('', views.view_dashboard, name='dashboard'),
    path('members', views.view_members, name='members'),
    path('members/<str:username>', views.view_profile, name='profile'),
    path('post/ajax/invite', views.postInvite, name="post_invite"),
]