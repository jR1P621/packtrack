from json import JSONDecoder
from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

import requests
import re

from .. import models, settings
from core.api.serializers.common import NestedDynamicFieldsModelSerializer


class KennelSerializer(NestedDynamicFieldsModelSerializer,
                       serializers.HyperlinkedModelSerializer):
    '''
    Serializer for creating and modifying Kennels.

    Kennel city field uses GeoNames database for verification:
    https://data.opendatasoft.com/explore/dataset/geonames-all-cities-with-a-population-500%40public/
    '''

    membership = serializers.SerializerMethodField()

    class Meta:
        model = models.Kennel
        fields = ['url', 'name', 'acronym', 'city', 'membership']
        read_only_fields = ['membership']

    def get_membership(self, instance):
        return MembershipSerializer(instance.memberships,
                                    many=True,
                                    context=self.context,
                                    fields=[
                                        'url', 'is_approved', 'is_admin',
                                        'user__url', 'user__username',
                                        'user__profile__hash_name'
                                    ]).data

    def parse_city(record: dict) -> str:
        '''
        Returns a readable string from a GeoNames database record
        '''
        city: str = record['record']['fields']['name']
        region: str = record['record']['fields']['admin1_code']
        country: str = record['record']['fields']['country']

        # Only add region if it is non-numeric
        if re.search('\d+', region):
            return f'{city}, {country}'
        else:
            return f'{city}, {region}, {country}'

    def get_cities(value: str) -> dict:
        '''
        Make a GET request to GeoNames database 
        '''

        # Parse input string by spaces, commas, semicolons
        strs = re.split('[\s,;]+', value)

        url = 'https://data.opendatasoft.com/api/v2/catalog/datasets/geonames-all-cities-with-a-population-500@public/records?select=name,country,admin1_code&where='

        # Build request url
        for str in strs:
            url += f'(name like "*{str}*" OR country like "*{str}*" OR admin1_code like "*{str}*")'
            if str is not strs[-1]:  # not last search term
                url += " AND "
        url = url + '&limit = 10'

        response = requests.get(url)
        return JSONDecoder().decode(response.content.decode("utf-8"))

    def validate_city(self, value: str) -> str:
        '''
        Checks input value against GeoNames database and returns a formatted string.
        '''
        if not value:
            raise serializers.ValidationError(_('City cannot be empty'))

        response = KennelSerializer.get_cities(value)
        try:
            records = response['records']
        except KeyError:  # Problem communicating with database
            raise serializers.ValidationError(
                _('Kennel creation is currently down for maintenance'))

        # search returned 1 result
        if len(records) == 1:
            return KennelSerializer.parse_city(records[0])
        # search didn't return any results
        elif len(records) == 0:
            raise serializers.ValidationError(_("Could not find city"))
        # search returned multiple results
        else:
            cities = []
            for record in records:
                cities.append(KennelSerializer.parse_city(record))
            raise serializers.ValidationError(
                [_("Multiple matching cities found"), cities])

    def create(self, validated_data):
        '''
        Extends super method to create a membership for the kennel creator
        '''
        kennel: models.Kennel = super().create(validated_data)
        models.Membership.objects.create(user=self.context['request'].user,
                                         kennel=kennel,
                                         is_approved=True,
                                         is_admin=True)
        return kennel


class MembershipSerializer(NestedDynamicFieldsModelSerializer,
                           serializers.HyperlinkedModelSerializer):

    kennel = KennelSerializer(fields=['url', 'name', 'acronym'])
    from core.api.serializers.serializers import UserSerializer
    user = UserSerializer(
        fields=['url', 'username', 'profile__url', 'profile__hash_name'])

    class Meta:
        model = models.Membership
        fields = ['url', 'user', 'kennel', 'is_approved', 'is_admin']
        read_only_fields = ['url', 'user', 'kennel', 'is_approved', 'is_admin']


class MembershipCreateSerializer(NestedDynamicFieldsModelSerializer,
                                 serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Membership
        fields = ['url', 'user', 'kennel', 'is_approved', 'is_admin']
        read_only_fields = ['url', 'user', 'is_approved', 'is_admin']


class MembershipUpdateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Membership
        fields = ['url', 'user', 'kennel', 'is_approved', 'is_admin']
        read_only_fields = ['user', 'kennel', 'is_admin']


class ConsensusSerializer(NestedDynamicFieldsModelSerializer,
                          serializers.HyperlinkedModelSerializer):

    kennel = KennelSerializer(fields=['url', 'name', 'acronym'],
                              read_only=True)
    event = serializers.SerializerMethodField()
    from core.api.serializers.serializers import UserSerializer
    membership = MembershipSerializer(fields=[
        'url', 'user__url', 'user__username', 'user__profile__hash_name'
    ],
                                      read_only=True)
    initiator = UserSerializer(
        fields=['url', 'username', 'profile__hash_name'], read_only=True)

    class Meta:
        model = models.Consensus
        fields = ['url', 'initiator', 'kennel', 'type', 'membership', 'event']
        read_only_fields = ['url', 'initiator', 'membership', 'event']

    def get_event(self, instance):
        from events.api.serializers import EventSerializer
        return EventSerializer(instance=instance.event,
                               context=self.context,
                               fields=[
                                   'url', 'name', 'date', 'host__url',
                                   'host__name', 'host__acronym'
                               ]).data


class ConsensusCreateSerializer(NestedDynamicFieldsModelSerializer,
                                serializers.HyperlinkedModelSerializer):

    type = serializers.ChoiceField([
        (key, value) for key, value in settings.CONSENSUS_TYPES.items()
    ])

    class Meta:
        model = models.Consensus
        fields = ['url', 'initiator', 'kennel', 'type', 'membership', 'event']
        read_only_fields = ['url', 'initiator']

    def create(self, validated_data):
        '''
        Extends super method to create a consensus item
        '''
        if not self.context['request'].user in validated_data[
                'kennel'].get_kennel_admins():
            raise PermissionError
        elif self.validated_data['membership'] and self.validated_data[
                'membership'].kennel != self.validated_data['kennel']:
            raise serializers.ValidationError
        consensus: models.Consensus = super().create(validated_data)
        return consensus


class ConsensusVoteSerializer(serializers.HyperlinkedModelSerializer):

    consensus = ConsensusSerializer(fields=[
        'url', 'type', 'kennel_url', 'kennel__name', 'initiator__url',
        'initiator__username', 'initiator__profile__url',
        'initiator__profile__hash_name', 'membership__url',
        'membership__user__url', 'membership__user__username',
        'membership__user__profile__url',
        'membership__user__profile__hash_name', 'event'
    ],
                                    read_only=True)

    class Meta:
        model = models.ConsensusVote
        fields = ['url', 'consensus', 'voter', 'vote']
        read_only_fields = ['url', 'consensus', 'voter']


class LegacyLongevitySerializer(serializers.HyperlinkedModelSerializer):

    from core.api.serializers.serializers import UserSerializer
    user = UserSerializer(fields=['username', 'profile__hash_name'],
                          read_only=True)
    kennel = KennelSerializer(fields=['name', 'acronym'], read_only=True)

    class Meta:
        model = models.LegacyLongevity
        fields = ['url', 'user', 'kennel', 'count', 'hares']
        read_only_fields = ['url', 'user', 'kennel']


class LegacyLongevityCreateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.LegacyLongevity
        fields = ['url', 'user', 'kennel', 'count', 'hares']
