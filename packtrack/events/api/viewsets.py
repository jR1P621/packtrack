from rest_framework import viewsets, permissions, filters, status
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum

from kennels.models import Kennel, LegacyLongevity, Membership

from .. import models
from . import serializers
from core.api.viewsets.common import MultiClassModelViewSet


class EventPermission(permissions.BasePermission):
    '''
    Permissions for Event viewset

    CREATE:
    Kennel admins can create events
        (this permission resticts creation to any user that has admin rights to
        any kennel.  Kennel-level restrictions are implemented in EventCreateSerializer)
    
    UPDATE:
    Event name can be changed by event host admins

    DESTROY:
    Kennel admins can destroy events their kennel is hosting iff
        there are no claimed attendance records for the event
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action == 'create':  # user is admin for any kennel
            return Membership.objects.filter(user=request.user,
                                             is_admin=True).count() > 0
        elif view.action in [
                'list', 'retrieve', 'update', 'partial_update', 'destroy'
        ]:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        elif view.action == 'retrieve':
            return True
        elif view.action == 'destroy':
            return (request.user in obj.host.get_kennel_admins()) and (
                obj.attendance.filter(user__isnull=False).count() == 0)
        elif view.action in ['update', 'partial update']:
            return request.user in obj.host.get_kennel_admins()
        else:
            return False


class EventViewSet(MultiClassModelViewSet):
    '''
    API endpoint for Event model
    '''
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    serializer_action_classes = {'create': serializers.EventCreateSerializer}
    permission_classes = [EventPermission]
    http_method_names = [
        'get', 'head', 'put', 'patch', 'options', 'post', 'delete'
    ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'name', 'date', 'host__name', 'host__acronym', 'kennels__name',
        'kennels__acronym', 'id'
    ]
    search_fields = [
        'name', 'date', 'host__name', 'host__acronym', 'kennels__name',
        'kennels__acronym'
    ]


class AttendPermission(permissions.BasePermission):
    '''
    Permissions for Attend viewset

    CREATE:
    Kennel admins can create attendance records
        (this permission resticts creation to any user that has admin rights to
        any kennel.  Kennel-level restrictions are implemented in AttendCreateSerializer)

    UPDATE:
    For unclaimed Attend (user is null): `user`, `unclaimed_name`, `is_hare` can be modified
        by Attend event host admins
    For claimed Attend, `is_hare` can be modified by Attend event host admins

    DESTROY:
    An unclaimed Attend (user is null) can be deleted by an event host admin.
    A claimed Attend can only be deleted by the Attend user
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action == 'create':
            return Membership.objects.filter(user=request.user,
                                             is_admin=True).count() > 0
        elif view.action in [
                'list', 'retrieve', 'update', 'partial_update', 'destroy',
                'count'
        ]:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        elif view.action == 'retrieve':
            return True
        elif view.action == 'destroy':
            return obj.user == request.user or (
                obj.unclaimed_name
                and request.user in obj.event.host.get_kennel_admins())
        elif view.action in ['update', 'partial update']:
            return request.user in obj.event.host.get_kennel_admins()
        else:
            return False


class AttendViewSet(MultiClassModelViewSet):
    '''
    API endpoint for Attend model
    '''
    queryset = models.Attend.objects.all().order_by('-event__date')
    serializer_class = serializers.AttendSerializer
    serializer_action_classes = {
        'create': serializers.AttendCreateSerializer,
    }
    permission_classes = [AttendPermission]
    http_method_names = [
        'get', 'head', 'put', 'patch', 'options', 'post', 'delete'
    ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'is_hare', 'user__username', 'user__profile__hash_name', 'event__name',
        'event__host__name', 'event__host__acronym', 'event__kennels__name',
        'event__kennels__acronym', 'id'
    ]
    search_fields = [
        'user__username', 'user__profile__hash_name', 'event__name',
        'event__host__name', 'event__host__acronym', 'event__kennels__name',
        'event__kennels__acronym', 'event__date'
    ]

    def get_serializer_class(self):
        '''
        Restricts admin `update` rights for claimed attendance records
        '''
        try:
            instance = self.get_object()
        except:
            return super().get_serializer_class()
        else:
            if self.action not in ['update', 'partial_update']:
                return super().get_serializer_class()
            if instance.user:
                return serializers.AttendModifyClaimedSerializer
            else:
                return serializers.AttendModifyUnclaimedSerializer

    @action(detail=False)
    def count(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        count = queryset.count()
        legacy_queryset = LegacyLongevity.objects.filter(
            user__username=request.GET['user__username'])
        legacy_count = legacy_queryset.aggregate(Sum('count'))
        legacy_hares = legacy_queryset.aggregate(Sum('hares'))
        if 'is_hare' in request.GET.keys(
        ) and request.GET['is_hare'] and legacy_hares['hares__sum']:
            count += legacy_hares['hares__sum']
        elif legacy_count['count__sum']:
            count += legacy_count['count__sum']
        content = {'count': count}
        return Response(content, status=status.HTTP_200_OK)


class LongevityRecordPermission(permissions.BasePermission):
    '''
    Permissions for LongevityRecord viewset

    UPDATE:
    Longevity kennel admins can modify `is_longevity`
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action in [
                'list', 'retrieve', 'update', 'partial_update', 'count'
        ]:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        elif view.action == 'retrieve':
            return True
        elif view.action in ['update', 'partial update']:
            return request.user in obj.longevity.kennel.get_kennel_admins()
        else:
            return False


class LongevityRecordViewSet(viewsets.ModelViewSet):
    '''
    API endpoint for LongevityRecord model
    '''
    queryset = models.LongevityRecord.objects.all().order_by('longevity')
    serializer_class = serializers.LongevityRecordSerializer
    permission_classes = [LongevityRecordPermission]
    http_method_names = ['get', 'head', 'put', 'patch', 'options']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'attend__user', 'attend__user__username',
        'attend__user__profile__hash_name', 'longevity__kennel__name',
        'longevity__kennel__acronym', 'id'
    ]
    search_fields = [
        'attend__user__username', 'attend__user__profile__hash_name',
        'longevity__kennel__name', 'longevity__kennel__acronym'
    ]

    @action(detail=False)
    def count(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        legacy_queryset = LegacyLongevity.objects.filter(
            user__username=request.GET['attend__user__username'])
        kennels = Kennel.objects.filter(
            id__in=[lr.longevity.kennel.id for lr in queryset])
        content = {'results': []}
        for k in kennels:
            legacy_longevity = legacy_queryset.filter(kennel=k)
            if legacy_longevity.exists():
                legacy_longevity = legacy_longevity.get()
                legacy_count = legacy_longevity.count
                legacy_hares = legacy_longevity.hares
            else:
                legacy_count = 0
                legacy_hares = 0
            content['results'].append({
                'kennel__name':
                k.name,
                'run_count':
                queryset.filter(longevity__kennel=k).count(),
                'hare_count':
                queryset.filter(longevity__kennel=k,
                                attend__is_hare=True).count(),
                'legacy_run_count':
                legacy_count,
                'legacy_hare_count':
                legacy_hares
            })
        content['results'] = sorted(
            content['results'],
            key=lambda r: r['run_count'] + r['hare_count'] + r[
                'legacy_run_count'] + r['legacy_hare_count'],
            reverse=True)
        content['count'] = len(content['results'])
        return Response(content, status=status.HTTP_200_OK)


class LongevityViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint for Longevity model
    '''
    queryset = models.Longevity.objects.all().order_by('event')
    serializer_class = serializers.LongevitySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'head', 'options']

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'event__name', 'event__host__name', 'event__host__acronym',
        'kennel__name', 'kennel__acronym', 'id'
    ]
    search_fields = [
        'event__name', 'event__host__name', 'event__host__acronym',
        'kennel__name', 'kennel__acronym'
    ]


class AttendClaimPermission(permissions.BasePermission):
    '''
    Permissions for AttendClaim viewset

    DESTROY:
    Users can delete their own attendance claims.
    Attend host admins can indirectly delete claims by adding user to attend
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action in ['create', 'list', 'retrieve', 'destroy']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        elif view.action == 'retrieve':
            return True
        elif view.action == 'destroy':
            return request.user == obj.claimant
        else:
            return False


class AttendClaimViewSet(MultiClassModelViewSet):
    '''
    API endpoint for AttendClaim
    '''
    queryset = models.AttendClaim.objects.all()
    serializer_class = serializers.AttendClaimSerializer
    serializer_action_classes = {
        'create': serializers.AttendClaimCreateSerializer
    }
    permission_classes = [AttendClaimPermission]
    http_method_names = ['get', 'head', 'options', 'post', 'delete']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'claimant__username', 'claimant__profile__hash_name',
        'attend__event__name', 'attend__event__host__name',
        'attend__event__host__acronym', 'id'
    ]
    search_fields = [
        'claimant__username', 'claimant__profile__hash_name',
        'attend__event__name', 'attend__event__host__name',
        'attend__event__host__acronym'
    ]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(claimant=self.request.user)
