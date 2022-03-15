from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from random import getrandbits
from django.utils.translation import gettext_lazy as _

import datetime, base64

from ... import models, settings
from .common import NestedDynamicFieldsModelSerializer


class UserCreateSerializer(serializers.HyperlinkedModelSerializer):
    '''
    Allows anon (not logged in) users to register a new account.
    '''

    password = serializers.CharField(
        write_only=True,
        help_text=password_validation.password_validators_help_text_html(),
        style={'input_type': 'password'})
    invite_code = serializers.CharField(
        label=_("Invite Code"),
        help_text=
        _("If creating a new account, enter a valid invite code.\nIf you don't have one, ask a current member to send you one."
          ),
    )
    username = serializers.CharField(
        help_text=User._meta.get_field('username').help_text)

    class Meta:
        model = User
        fields = ['url', 'username', 'password', 'invite_code']
        read_only_fields = ['url']
        depth = 0

    def validate_invite_code(self, value):
        '''
        Checks that invite code exists and is not expired or used
        '''
        invite = models.InviteCode.objects.filter(code=value)
        # check if invite exists
        if invite.count() == 0:
            raise serializers.ValidationError("Invalid invite code")

        # check that invite is not already used and is not expired
        invite = invite.get()
        if invite.receiver or invite.expiration < datetime.date.today():
            raise serializers.ValidationError("Invalid invite code")
        return value

    def validate_password(self, value):
        '''
        Validates password agains django.contrib.auth password validation
        '''
        if value:
            try:
                password_validation.validate_password(value, self.instance)
            except ValidationError as error:
                raise serializers.ValidationError(error)
        return value

    def create(self, validated_data):
        '''
        Creates the new user account
        '''

        invite: models.InviteCode = models.InviteCode.objects.get(
            code=validated_data.pop('invite_code'))
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        invite.receiver = user
        invite.save()
        return user


class UserSerializer(NestedDynamicFieldsModelSerializer,
                     serializers.HyperlinkedModelSerializer):
    '''
    Serializer for browsing/editing User model
    '''

    password = serializers.CharField(
        write_only=True,
        help_text=password_validation.password_validators_help_text_html(),
        style={'input_type': 'password'})
    membership = serializers.SerializerMethodField()
    from profiles.api.serializers import ProfileSerializer
    profile = ProfileSerializer(fields=['url', 'hash_name', 'avatar'])

    class Meta:
        model = User
        fields = [
            'url', 'username', 'email', 'password', 'profile', 'invite_code',
            'membership'
        ]
        read_only_fields = [
            'url', 'profile', 'password', 'invite_code', 'membership'
        ]

    def get_membership(self, instance):
        '''
        Gets nested serializer with custom depth and fields
        '''
        from kennels.models import Membership
        from kennels.api.serializers import MembershipSerializer
        membership = Membership.objects.filter(user=instance)
        return MembershipSerializer(membership,
                                    many=True,
                                    context=self.context,
                                    fields=[
                                        'url', 'is_admin', 'is_approved',
                                        'kennel', 'kennel__name',
                                        'kennel__acronym'
                                    ]).data

    def validate_password(self, value):
        '''
        Validates password agains django.contrib.auth password validation
        '''
        if value:
            try:
                password_validation.validate_password(value, self.instance)
            except ValidationError as error:
                raise serializers.ValidationError(error)
        return value


class InviteSerializer(serializers.HyperlinkedModelSerializer):
    '''
    serializer for InviteCode API endpoint.
    '''

    receiver = UserSerializer(fields=['url', 'username', 'profile__hash_name'],
                              read_only=True)

    class Meta:
        model = models.InviteCode
        fields = ['code', 'expiration', 'receiver', 'creator']
        read_only_fields = ['code', 'expiration', 'receiver', 'creator']

    def create(self, validated_data):
        '''
        Allows users to generate upto INVITE_CODE_LIMIT number of invite codes
        '''

        # Check that limit is not exceeded
        limit = settings.INVITE_CODE_LIMIT
        member_invites = models.InviteCode.objects.filter(
            creator=validated_data['creator'])
        open_count = member_invites.filter(receiver__isnull=True).count()
        if open_count >= limit:
            error = {'message': 'Invite code limit exceeded'}
            raise serializers.ValidationError(error)

        # Generate invite code
        while True:  # Loop if collision (very unlikely)
            # 48bit base64 creates 8char str
            new_code_int = getrandbits(48)
            new_code = base64.b64encode(new_code_int.to_bytes(
                6, 'big')).decode("utf-8")
            # break if code is unique
            if models.InviteCode.objects.filter(code=new_code).count() == 0:
                break

        return models.InviteCode.objects.create(
            creator=validated_data['creator'],
            code=new_code,
        )


class InviteSerializerAdmin(serializers.HyperlinkedModelSerializer):
    '''
    Serializer for InviteCode model
    '''

    class Meta:
        model = models.InviteCode
        fields = ['code', 'expiration', 'receiver', 'creator']
