from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    member_user_account = models.OneToOneField(User, on_delete=models.CASCADE)
    member_avatar = models.ImageField(null=True)
    # member_kennels = models.ManyToManyField('kennels.Kennel',
    #                                         through='kennels.KennelMembership')
    member_hash_name = models.CharField(max_length=64)
    member_email = models.EmailField(null=True)
    # member_membership_requests = models.ManyToManyField(
    #     'kennels.Kennel', through='MembershipRequest')


class MemberURLs(models.Model):
    url = models.URLField()
    url_member = models.ForeignKey(Member, on_delete=models.CASCADE)
    url_desc = models.CharField(max_length=32)


class MembershipRequest(models.Model):
    request_member = models.ForeignKey(Member, on_delete=models.CASCADE)
    request_kennel = models.ForeignKey('kennels.Kennel',
                                       on_delete=models.CASCADE)


class InviteCode(models.Model):
    invite_creator = models.ForeignKey(Member,
                                       on_delete=models.SET_NULL,
                                       null=True,
                                       related_name='invite_creator')
    invite_code = models.CharField(max_length=8)
    invite_expiration = models.DateField()
    invite_receiver = models.ForeignKey(Member,
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        related_name='invite_receiver')
