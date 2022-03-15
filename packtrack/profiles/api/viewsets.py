from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .. import models
from . import serializers


class ProfilePermission(permissions.BasePermission):
    '''
    Permissions for Profile viewset

    UPDATE:
    Profile user can update their own profile
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action in ['list', 'retrieve', 'update', 'partial_update']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        elif view.action == 'retrieve':
            return True
        elif view.action in ['update', 'partial_update']:
            return request.user == obj.user
        else:
            return False


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows member profiles to be viewed or edited.
    """
    queryset = models.Profile.objects.all().order_by('hash_name')
    serializer_class = serializers.ProfileSerializer
    permission_classes = [ProfilePermission]
    http_method_names = ['get', 'head', 'put', 'patch', 'options']
