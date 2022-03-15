from django.db.utils import IntegrityError
from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

from .. import models
from core.api.serializers.serializers import UserSerializer
from core.api.serializers.common import NestedDynamicFieldsModelSerializer
from kennels.api.serializers import KennelSerializer


class EventSerializer(NestedDynamicFieldsModelSerializer,
                      serializers.HyperlinkedModelSerializer):
    '''
    
    '''
    host = KennelSerializer(fields=['url,', 'name', 'acronym'], read_only=True)
    kennels = KennelSerializer(fields=['url', 'name', 'acronym'],
                               many=True,
                               read_only=True)
    attendance = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = ['url', 'id', 'name', 'date', 'host', 'attendance', 'kennels']
        read_only_fields = [
            'url', 'id', 'date', 'host', 'attendance', 'kennels'
        ]

    def get_attendance(self, instance):
        # get kennels where user is admin
        return AttendSerializer(instance.attendance.order_by('user'),
                                fields=[
                                    'url', 'is_hare', 'unclaimed_name',
                                    'user__url', 'user__username',
                                    'user__profile__hash_name'
                                ],
                                many=True,
                                context=self.context).data


class EventCreateSerializer(serializers.HyperlinkedModelSerializer):
    '''
    Serializer for Event creation.
    Provides proper fields and kennel-level permissions
    '''

    date = serializers.DateField()

    class Meta:
        model = models.Event
        fields = ['name', 'date', 'host']

    def create(self, validated_data):
        if self.context['request'].user in validated_data[
                'host'].get_kennel_admins():
            return super().create(validated_data)
        raise exceptions.PermissionDenied


class LongevitySerializer(NestedDynamicFieldsModelSerializer,
                          serializers.HyperlinkedModelSerializer):

    kennel = KennelSerializer(fields=['url', 'name', 'acronym'])
    event = EventSerializer(
        fields=['url', 'name', 'host__url', 'host__name', 'host__acronym'])

    class Meta:
        model = models.Longevity
        fields = ['url', 'kennel', 'event']
        read_only_fields = ['url', 'kennel', 'event']


class AttendSerializer(NestedDynamicFieldsModelSerializer,
                       serializers.HyperlinkedModelSerializer):

    user = UserSerializer(fields=['url', 'username', 'profile__hash_name'],
                          read_only=True)

    longevity_records = serializers.SerializerMethodField()
    event = EventSerializer(fields=[
        'url', 'id', 'name', 'date', 'host__url', 'host__name', 'host__acronym'
    ])
    claimants = serializers.SerializerMethodField()

    class Meta:
        model = models.Attend
        fields = [
            'url', 'event', 'user', 'unclaimed_name', 'is_hare',
            'longevity_records', 'claimants'
        ]
        read_only_fields = [
            'event', 'user', 'unclaimed_name', 'is_hare', 'longevity_records',
            'claimants'
        ]

    def get_longevity_records(self, instance):
        return LongevityRecordSerializer(instance=instance.longevity_records,
                                         context=self.context,
                                         fields=[
                                             'url', 'longevity',
                                             'longevity__kennel__url',
                                             'longevity__kennel__name',
                                             'longevity__kennel__acronym'
                                         ],
                                         many=True).data

    def get_claimants(self, instance):
        return UserSerializer(instance=instance.claimants,
                              context=self.context,
                              fields=[
                                  'url',
                                  'username',
                                  'profile__hash_name',
                              ],
                              many=True).data


class AttendCreateSerializer(NestedDynamicFieldsModelSerializer,
                             serializers.HyperlinkedModelSerializer):
    '''
    Serializer for Attend creation.
    Provides proper fields and kennel-level permissions
    '''

    class Meta:
        model = models.Attend
        fields = ['url', 'event', 'user', 'unclaimed_name', 'is_hare']

    def create(self, validated_data):
        if self.context['request'].user in validated_data[
                'event'].host.get_kennel_admins():
            return super().create(validated_data)
        raise exceptions.PermissionDenied


class AttendModifyClaimedSerializer(NestedDynamicFieldsModelSerializer,
                                    serializers.HyperlinkedModelSerializer):
    '''
    Serializer for claimed Attend modification.
    Restricts writable fields
    '''

    class Meta:
        model = models.Attend
        fields = ['url', 'event', 'user', 'is_hare']
        read_only_fields = ['event', 'user']


class AttendModifyUnclaimedSerializer(NestedDynamicFieldsModelSerializer,
                                      serializers.HyperlinkedModelSerializer):
    '''
    Serializer for claimed Attend modification.
    '''

    class Meta:
        model = models.Attend
        fields = ['url', 'event', 'user', 'unclaimed_name', 'is_hare']
        read_only_fields = ['event']


class LongevityRecordSerializer(NestedDynamicFieldsModelSerializer,
                                serializers.HyperlinkedModelSerializer):

    longevity = LongevitySerializer(fields=[
        'event__url', 'event__name', 'event__host__url', 'event__host__name',
        'event__host__acronym', 'kennel__url', 'kennel__name',
        'kennel__acronym'
    ],
                                    read_only=True)
    attend = AttendSerializer(fields=[
        'user__url', 'user__username', 'user__profile__hash_name',
        'unclaimed_name'
    ],
                              read_only=True)

    class Meta:
        model = models.LongevityRecord
        fields = ['url', 'longevity', 'is_longevity', 'attend']


class AttendClaimSerializer(serializers.HyperlinkedModelSerializer):

    attend = AttendSerializer(fields=[
        'url', 'event__url', 'event__name', 'event__date', 'event__host__url',
        'event__host__name', 'event__host__acronym', 'unclaimed_name'
    ])

    class Meta:
        model = models.AttendClaim
        fields = ['url', 'attend', 'claimant']
        read_only_fields = ['claimant']


class AttendClaimCreateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.AttendClaim
        fields = ['attend', 'claimant']
        read_only_fields = ['claimant']

    def create(self, validated_data):

        # if the attend is already claimed
        if validated_data['attend'].user:
            raise IntegrityError
        # if the claimant already has an attend for this event
        if models.Attend.objects.filter(
                user=self.context['request'].user,
                event=validated_data['attend'].event).count() > 0:
            raise IntegrityError

        return super().create(validated_data)