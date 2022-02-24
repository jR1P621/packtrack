from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import datetime


class Member(models.Model):
    member_user_account = models.OneToOneField(User, on_delete=models.CASCADE)
    member_avatar = models.ImageField(null=True)
    member_hash_name = models.CharField(max_length=64)
    member_email = models.EmailField(null=True)

    def __str__(self):
        return self.member_user_account.username


class MemberURLs(models.Model):
    url = models.URLField()
    url_member = models.ForeignKey(Member, on_delete=models.CASCADE)
    url_desc = models.CharField(max_length=32)


class InviteCode(models.Model):
    invite_creator = models.ForeignKey(Member,
                                       on_delete=models.SET_NULL,
                                       null=True,
                                       related_name='invite_creator')
    invite_code = models.CharField(max_length=8, unique=True)
    invite_expiration = models.DateField(default=datetime.date.today() +
                                         datetime.timedelta(days=7),
                                         null=True)
    invite_receiver = models.ForeignKey(Member,
                                        on_delete=models.CASCADE,
                                        null=True,
                                        related_name='invite_receiver')

    # def __str__(self):
    #     return ','.join([
    #         self.invite_code,
    #         str(self.invite_expiration),
    #         str(self.invite_creator),
    #         str(self.invite_receiver)
    #     ])


# create associated member object when user account is created
@receiver(post_save, sender=User)
def create_member(sender, instance, created, **kwargs):
    if created:
        Member.objects.create(
            member_user_account=instance,
            member_hash_name=instance.username,
        )


@receiver(pre_delete, sender=Member)
def delete_unused_invites(sender, instance, **kwargs):
    try:
        unused_invites = InviteCode.objects.filter(
            invite_creator=instance, invite_receiver__isnull=True)
        unused_invites.delete()
    except InviteCode.DoesNotExist:
        pass