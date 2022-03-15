from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from .. import models
from core.api.serializers.common import NestedDynamicFieldsModelSerializer


class ProfileSerializer(NestedDynamicFieldsModelSerializer,
                        serializers.HyperlinkedModelSerializer):

    email = serializers.EmailField(source='user.email',
                                   allow_blank=True,
                                   allow_null=True)

    class Meta:
        model = models.Profile
        fields = ['url', 'user', 'hash_name', 'avatar', 'email']
        read_only_fields = ['url', 'user']

    def update(self, instance, validated_data):

        # save email to user account
        user_data = validated_data.pop('user')
        instance.user.email = user_data.get('email', instance.user.email)
        instance.user.save()

        super().update(instance, validated_data)
