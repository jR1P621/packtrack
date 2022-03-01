from hashlib import md5, sha256
from PIL import Image
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import datetime

MAX_AVATAR_SIZE = 800


def avatar_upload(instance, filename):
    '''
    Saves profile picture as a SHA256 hex digest.
    '''
    return f'member_avatars/{sha256((filename+datetime.datetime.now().ctime()).encode()).hexdigest()}'


class Member(models.Model):
    '''
    Model for member.  Extends auth.models.User model.
    '''
    member_user_account = models.OneToOneField(User, on_delete=models.CASCADE)
    member_avatar = models.ImageField(null=True, upload_to=avatar_upload)
    member_hash_name = models.CharField(max_length=64)
    member_email = models.EmailField(null=True)
    member_kennels = models.ManyToManyField('kennels.Kennel',
                                            blank=True,
                                            through='kennels.KennelMembership')

    def __str__(self) -> str:
        return self.member_user_account.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Rescale avatar to max 800px
        if self.member_avatar:
            image = Image.open(self.member_avatar)
            (width, height) = image.size
            if (MAX_AVATAR_SIZE / width < MAX_AVATAR_SIZE / height):
                factor = MAX_AVATAR_SIZE / height
            else:
                factor = MAX_AVATAR_SIZE / width
            size = (width / factor, height / factor)
            image = image.resize(size, Image.ANTIALIAS)
            image.save(self.member_avatar.path)


class MemberURLs(models.Model):
    '''
    STUB. Member links.  Can be used for social media.
    '''
    url = models.URLField()
    url_member = models.ForeignKey(Member, on_delete=models.CASCADE)
    url_desc = models.CharField(max_length=32)


class InviteCode(models.Model):
    '''
    An invite code needed for new users to register.
    '''
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


@receiver(post_save, sender=User)
def create_member(sender, instance, created, **kwargs) -> None:
    '''
    Creates an associated Member instance when a new User is created.
    '''
    if created:
        Member.objects.create(
            member_user_account=instance,
            member_hash_name=instance.username,
        )


@receiver(pre_delete, sender=Member)
def delete_unused_invites(sender, instance, **kwargs) -> None:
    '''
    Deletes unused InviteCodes when a user deletes their account.
    '''
    try:
        unused_invites = InviteCode.objects.filter(
            invite_creator=instance, invite_receiver__isnull=True)
        unused_invites.delete()
    except InviteCode.DoesNotExist:
        pass