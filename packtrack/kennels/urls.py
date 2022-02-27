from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.kennelListView.as_view()), name='kennels'),
    path('mykennels',
         login_required(views.kennelListView.as_view(user_kennels=True))),
    path('profile/<str:kennel_name>', views.view_kennel,
         name='kennel_profile'),
    path('create_kennel', views.view_create_kennel, name='create_kennel'),
]