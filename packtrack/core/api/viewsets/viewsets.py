from urllib.request import Request
from django.shortcuts import redirect
from rest_framework import viewsets, permissions, throttling, filters, status
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login, authenticate
from django_filters.rest_framework import DjangoFilterBackend

from ..serializers import serializers
from .common import MultiClassModelViewSet
from ... import models


class UserPermission(permissions.BasePermission):
    '''
    Permissions for User viewset

    CREATE:
    Unauthenticated users can create accounts.

    LIST:
    All users can list
        (Unauthenticated users must have list permission to see the create form in
        django rest framework html portal (bug?). The viewset restricts the list 
        queryset to an emptyset)

    UPDATE:
    Users can modify their own account
    '''

    def has_permission(self, request, view):
        if view.action == 'create':
            return not request.user.is_authenticated
        elif view.action == 'list':
            return True
        elif view.action in ['retrieve', 'update', 'partial_update']:
            return request.user.is_authenticated
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if view.action == 'retrieve':
            return request.user.is_authenticated
        elif view.action in ['update', 'partial_update']:
            return obj == request.user
        else:
            return False


class UserViewSet(MultiClassModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by('username')
    serializer_class = serializers.UserSerializer
    serializer_action_classes = {'create': serializers.UserCreateSerializer}
    http_method_names = ['get', 'head', 'put', 'patch', 'options', 'post']
    permission_classes = [UserPermission]
    throttle_classes = [throttling.AnonRateThrottle]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'username', 'email', 'profile__hash_name', 'kennels__name',
        'kennels__acronym', 'id'
    ]
    search_fields = [
        'username', 'email', 'profile__hash_name', 'kennels__name',
        'kennels__acronym'
    ]

    def get_queryset(self):
        '''
        Returns none if user is not authenticated
        '''
        if not self.request.user.is_authenticated:
            return User.objects.none()
        return User.objects.all()

    def create(self, request, *args, **kwargs) -> Response:
        '''
        Attempts to log user in or tries to create new account.
        '''

        serializer = self.get_serializer(data=request.data)

        # attempt login
        user = authenticate(username=serializer.initial_data['username'],
                            password=serializer.initial_data['password'])
        if user is not None:
            login(request, user)
            headers = self.get_success_headers(serializer.initial_data)
            return Response({'message': _('login successful')},
                            status=status.HTTP_202_ACCEPTED,
                            headers=headers)
            # return Request({'message', 'Logged in'})
        # or attempt create account
        else:
            res = super().create(request, *args, **kwargs)
            # if successful, log new user in
            if res.status_code == 201:
                user = User.objects.get(username=res.data['username'])
                login(request, user)
            return res


class InviteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a invite codes to be viewed or created.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.InviteSerializer
    http_method_names = ['get', 'head', 'post', 'options']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'receiver__username', 'receiver__profile__hash_name', 'id'
    ]
    search_fields = ['receiver__username', 'receiver__profile__hash_name']

    def get_queryset(self):
        queryset = models.InviteCode.objects.filter(
            creator=self.request.user).order_by('expiration').order_by(
                'receiver')
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


# class InviteAdminViewSet(viewsets.ModelViewSet):
#     queryset = models.InviteCode.objects.all().order_by('creator')
#     serializer_class = serializers.InviteSerializerAdmin
#     permission_classes = [permissions.IsAdminUser]