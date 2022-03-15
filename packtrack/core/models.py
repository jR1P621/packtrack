from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import datetime

from . import settings


def default_invite_expiration():
    return datetime.date.today() + datetime.timedelta(
        days=settings.DEFAULT_INVITE_EXPIRATION_DAYS)


class InviteCode(models.Model):
    '''
    An invite code needed for new users to register.
    '''
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=8, unique=True)
    expiration = models.DateField(null=True, blank=True)
    receiver = models.OneToOneField(User,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    blank=True,
                                    related_name='invite_code')


@receiver(post_save, sender=InviteCode)
def set_expiration(sender, instance, created, **kwargs) -> None:
    '''
    Sets the expiration date for newly created InviteCodes.
    Removes expiration for used codes
    '''
    if created:
        instance.expiration = default_invite_expiration()
    elif instance.receiver and instance.expiration is not None:
        instance.expiration = None
    else:
        return
    instance.save()
