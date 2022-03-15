from django.db import IntegrityError, models
from django.db.models import Q, F
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User


# a hash event
class Event(models.Model):
    name = models.CharField(max_length=128)
    date = models.DateField()
    host = models.ForeignKey('kennels.Kennel',
                             on_delete=models.DO_NOTHING,
                             related_name='events')
    kennels = models.ManyToManyField('kennels.Kennel', through='Longevity')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'host'],
                                    name='unique_kennel_event')
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.host}"


# attendance record for member for specific event
class Attend(models.Model):
    event = models.ForeignKey(Event,
                              on_delete=models.CASCADE,
                              related_name='attendance')
    user = models.ForeignKey(User,
                             null=True,
                             on_delete=models.CASCADE,
                             related_name='attendance')
    unclaimed_name = models.CharField(max_length=64, null=True)
    is_hare = models.BooleanField(default=False)
    claimants = models.ManyToManyField(User, through='AttendClaim')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(user__isnull=False, unclaimed_name__isnull=True)
                | Q(user__isnull=True, unclaimed_name__isnull=False),
                name='attend_not_claimed_and_unclaimed'),
            models.UniqueConstraint(name='unique_claimed_attend',
                                    fields=('event', 'user'),
                                    condition=Q(unclaimed_name__isnull=True)),
            models.UniqueConstraint(name='unique_unclaimed_attend',
                                    fields=('event', 'unclaimed_name'),
                                    condition=Q(user__isnull=True))
        ]

    def __str__(self) -> str:
        if self.user:
            return f"(Claimed - {self.user}) - ({self.event})"
        else:
            return f"(Unclaimed - {self.unclaimed_name}) - ({self.event})"


class AttendClaim(models.Model):
    attend = models.ForeignKey(Attend, on_delete=models.CASCADE)
    claimant = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name='attend_claims')

    class Meta:
        constraints = [
            models.UniqueConstraint(name='unique_attend_claim',
                                    fields=('attend', 'claimant'))
        ]


# Allows kennels to count event attandance toward kennel longevity
class Longevity(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    kennel = models.ForeignKey('kennels.Kennel', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'kennel'],
                                    name='unique_longevity')
        ]

    def __str__(self) -> str:
        return f"({self.event}) - {self.kennel}"


# individual longevity record for each attendance record
class LongevityRecord(models.Model):
    attend = models.ForeignKey(Attend,
                               on_delete=models.CASCADE,
                               related_name='longevity_records')
    longevity = models.ForeignKey(Longevity, on_delete=models.CASCADE)
    is_longevity = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['attend', 'longevity'],
                                    name='unique_longevity_record')
        ]

    def __str__(self) -> str:
        return f"{self.attend} - {self.longevity.kennel}"


# Create a longevity object for the event host's kennel
@receiver(post_save, sender=Event)
def create_initial_longevity(sender, instance, created, **kwargs):
    if created:
        Longevity.objects.create(event=instance, kennel=instance.host)


# Create Logevity records for each Attend-Longevity pair
@receiver(post_save, sender=Attend)
def create_longevity_record_attend(sender, instance, created, **kwargs):
    if created:
        longevities = Longevity.objects.filter(event=instance.event)
        LongevityRecord.objects.bulk_create([
            LongevityRecord(attend=instance, longevity=l) for l in longevities
        ])


@receiver(post_save, sender=Longevity)
def create_longevity_record_longevity(sender, instance, created, **kwargs):
    if created:
        attends = Attend.objects.filter(event=instance.event)
        LongevityRecord.objects.bulk_create(
            [LongevityRecord(attend=a, longevity=instance) for a in attends])


@receiver(post_save, sender=AttendClaim)
def prevent_claim_of_claimed(sender, instance, created, **kwargs):
    if instance.attend.user:
        instance.delete()
        raise IntegrityError


@receiver(post_save, sender=Attend)
def delete_claims(sender, instance, created, **kwargs):
    if instance.user:
        AttendClaim.objects.filter(attend=instance).delete()