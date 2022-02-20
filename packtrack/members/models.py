from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Member(models.Model):
    member_user_account = models.OneToOneField(User, on_delete=models.CASCADE)
    member_avatar = models.ImageField(null=True)
    member_hash_name = models.CharField(max_length=64)
    member_email = models.EmailField(null=True)


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


# create associated member object when user account is created
@receiver(post_save, sender=User)
def create_member(sender, instance, created, **kwargs):
    if created:
        Member.objects.create(
            member_user_account=instance,
            member_hash_name=instance.username,
        )
