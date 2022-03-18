"""packtrack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from core.api.urls import router as core_router
from profiles.api.urls import router as profiles_router
from kennels.api.urls import router as kennels_router
from events.api.urls import router as events_router

router = routers.DefaultRouter()
router.registry.extend(core_router.registry)
router.registry.extend(profiles_router.registry)
router.registry.extend(kennels_router.registry)
router.registry.extend(events_router.registry)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('hashers/', include('profiles.urls')),
    path('kennels/', include('kennels.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
