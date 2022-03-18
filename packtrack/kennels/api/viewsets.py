from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend

from core.api.viewsets.common import MultiClassModelViewSet

from .. import models
from . import serializers

http_method_names = [
    'get', 'head', 'put', 'patch', 'options', 'post', 'delete'
]


class KennelPermission(permissions.BasePermission):
    '''
    Permissions for Kennel viewset

    CREATE:
    Anybody can create a kennel

    UPDATE:
    Kennel admins can make updates
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action in [
                'create', 'list', 'retrieve', 'update', 'partial_update'
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
            return request.user in obj.get_kennel_admins()
        else:
            return False


class KennelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows kennels to be created, viewed, or edited.
    """
    queryset = models.Kennel.objects.all().order_by('name').order_by(
        '-is_active')
    serializer_class = serializers.KennelSerializer
    permission_classes = [KennelPermission]
    http_method_names = ['get', 'head', 'put', 'patch', 'options', 'post']

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'name', 'acronym', 'city', 'is_active', 'members__username',
        'members__profile__hash_name', 'id'
    ]
    search_fields = [
        'name', 'acronym', 'city', 'members__username',
        'members__profile__hash_name'
    ]


class MembershipPermission(permissions.BasePermission):
    '''
    Permissions for Membership viewset

    CREATE:
    Anybody can create a Membership item for themselves for any kennel, 
        but the membership will initialize "unapproved".

    UPDATE:
    Membership kennel admins can approve unapproved memberships.

    DESTROY:
    Only Membership users can detroy their own memberships.
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action in [
                'create', 'list', 'retrieve', 'update', 'partial_update',
                'destroy'
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
            return request.user == obj.user and (
                not obj.is_admin or obj.kennel.get_kennel_admins().count() > 1)
        elif view.action in ['update', 'partial update']:
            return not obj.is_approved and request.user in obj.kennel.get_kennel_admins(
            )
        else:
            return False


class MembershipViewSet(MultiClassModelViewSet):
    """
    API endpoint that allows memberships to be viewed, created, approved, or deleted.
    """
    queryset = models.Membership.objects.all()
    serializer_class = serializers.MembershipSerializer
    serializer_action_classes = {
        'update': serializers.MembershipUpdateSerializer,
        'create': serializers.MembershipCreateSerializer
    }
    permission_classes = [MembershipPermission]
    http_method_names = [
        'get', 'head', 'options', 'post', 'delete', 'put', 'patch'
    ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'kennel__name', 'kennel__acronym', 'is_admin', 'is_approved',
        'user__username', 'user__profile__hash_name', 'id'
    ]
    search_fields = [
        'kennel__name', 'kennel__acronym', 'user__username',
        'user__profile__hash_name'
    ]

    def perform_create(self, serializer: serializers.MembershipSerializer):
        serializer.save(user=self.request.user)


class ConsensusPermission(permissions.BasePermission):
    '''
    Permissions for Consensus viewset

    CREATE & LIST:
    Kennel admins can create and list consensus items
        (this permission resticts creation/listing to any user that has admin rights to
        any kennel.  Kennel-level restrictions are implemented in viewset)

    RETRIEVE:
    Consensus kennel admins can retrieve items for their kennel

    DESTROY:
    Only Consensus initiators can detroy their own consensus items iff
        a final vote has not yet been reached.
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action in ['create', 'list', 'retrieve', 'destroy']:
            return models.Membership.objects.filter(user=request.user,
                                                    is_admin=True).exists()
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        elif view.action == 'retrieve':
            return request.user in obj.kennel.get_kennel_admins()
        elif view.action == 'destroy':
            return request.user == obj.initiator
        else:
            return False


class ConsensusViewSet(MultiClassModelViewSet):
    """
    API endpoint that allows consensus items to be viewed, created, or deleted.
    """

    queryset = models.Consensus.objects.all()
    serializer_class = serializers.ConsensusSerializer
    serializer_action_classes = {
        'create': serializers.ConsensusCreateSerializer
    }
    permission_classes = [ConsensusPermission]
    http_method_names = ['get', 'head', 'options', 'delete', 'post']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'kennel__name', 'kennel__acronym', 'type',
        'membership__user__username', 'membership__user__profile__hash_name',
        'initiator__username', 'initiator__profile__hash_name', 'event__name',
        'event__host__name', 'event__host__acronym', 'id'
    ]
    search_fields = [
        'kennel__name', 'kennel__acronym', 'membership__user__username',
        'membership__user__profile__hash_name', 'initiator__user__username',
        'initiator__user__profile__hash_name', 'event__name',
        'event__host__name', 'event__host__acronym'
    ]

    def list(self, request):
        '''
        Only list consensuses valid to user.
        A consensus will only appear if the user is an admin for the consensus kennel
        '''
        # get kennels where user is admin
        kennels = models.Kennel.objects.filter(memberships__user=request.user,
                                               memberships__is_admin=True)

        # serialize
        queryset = models.Consensus.objects.filter(
            kennel__in=kennels).order_by('kennel').order_by('type')
        serializer = serializers.ConsensusSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def perform_create(self, serializer: serializers.ConsensusSerializer):
        serializer.save(initiator=self.request.user)


class ConsensusVotePermission(permissions.BasePermission):
    '''
    Permissions for ConsensusVote viewset

    LIST:
    Kennel admins can list consensus vote items
        (this permission resticts listing to any user that has admin rights to
        any kennel.  User-level restrictions are implemented in viewset)

    RETRIEVE:
    A ConsensusVote voter can retrieve the item

    UPDATE:
    A ConsensusVote voter can change their vote
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action in ['list', 'retrieve', 'update', 'partial_update']:
            return models.Membership.objects.filter(user=request.user,
                                                    is_admin=True).exists()
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        elif view.action in ['retrieve', 'update', 'partial_update']:
            return request.user == obj.voter
        else:
            return False


class ConsensusVoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows consensus votes to be viewed and edited.
    """
    queryset = models.ConsensusVote.objects.all()
    serializer_class = serializers.ConsensusVoteSerializer
    permission_classes = [ConsensusVotePermission]
    http_method_names = ['get', 'head', 'options', 'put', 'patch']

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'consensus__kennel__name', 'consensus__kennel__acronym', 'id'
    ]
    search_fields = ['consensus__kennel__name', 'consensus__kennel__acronym']

    def list(self, request):
        '''
        Only list user's votes.
        '''
        queryset = models.ConsensusVote.objects.filter(
            voter=request.user).order_by('consensus__kennel').order_by(
                'consensus__type')
        serializer = serializers.ConsensusVoteSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


class LegacyLongevityPermission(permissions.BasePermission):
    '''
    Permissions for LegacyLongevity viewset

    CREATE:
    Kennel admins can create legacy longevity
        (this permission resticts creation to any user that has admin rights to
        any kennel.  Kennel-level restrictions are implemented in viewset)

    UPDATE:
    Kennel admins can modify legacy longevity for their kennel.
    '''

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif view.action == 'create':
            return models.Membership.objects.filter(user=request.user,
                                                    is_admin=True).exists()
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
            return request.user in obj.kennel.get_kennel_admins()
        else:
            return False


class LegacyLongevityViewSet(MultiClassModelViewSet):
    """
    API endpoint that allows legacy longevity to be viewed, created, or edited.
    """

    queryset = models.LegacyLongevity.objects.all()
    serializer_class = serializers.LegacyLongevitySerializer
    serializer_action_classes = {
        'create': serializers.LegacyLongevityCreateSerializer
    }
    permission_classes = [LegacyLongevityPermission]
    http_method_names = ['get', 'head', 'options', 'post', 'put', 'patch']
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        'kennel__name', 'kennel__acronym', 'user__username',
        'user__profile__hash_name'
    ]
    search_fields = [
        'kennel__name', 'kennel__acronym', 'user__username',
        'user__profile__hash_name'
    ]
