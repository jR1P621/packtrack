from django.db import models
from django.db.models.signals import pre_delete


# a hash event
class Event(models.Model):
    event_name = models.CharField(max_length=128)
    event_date = models.DateField()
    event_desc = models.TextField(blank=True)
    # event_hosts = models.ManyToManyField('kennels.Kennel', through='EventHost')
    # event_attendance = models.ManyToManyField('members.Member',
    #                                           through='EventAttend')


# event host record (events can have multiple hosts)
class EventHost(models.Model):
    host_kennel = models.ForeignKey('kennels.Kennel', on_delete=models.CASCADE)
    host_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    host_is_longevity = models.BooleanField()


# attendance record for member for specific event
class EventAttend(models.Model):
    attend_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attend_is_longevity = models.BooleanField()
    attend_is_hare = models.BooleanField()
    attend_note = models.TextField(blank=True)

    class Meta:
        abstract = True


class EventMemberAttend(EventAttend):
    attend_member = models.ForeignKey('members.Member',
                                      on_delete=models.CASCADE)
    attend_is_verified = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['attend_event', 'attend_member'],
                                    name='unique_member_attend')
        ]


class EventNonMemberAttend(EventAttend):
    attend_nonmember_name = models.CharField(max_length=32)
    attend_just_claim = models.ForeignKey('members.Member',
                                          on_delete=models.SET_NULL,
                                          null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['attend_event', 'attend_nonmember_name'],
                name='unique_nonmember_attend')
        ]


# if member deletes account or attendance record, create non-member record
# gives kennel more control over event headcounts
def delete_member_attend(sender, instance: EventMemberAttend, **kwargs):
    new_just_attend = EventNonMemberAttend(
        attend_event=instance.attend_event,
        attend_is_longevity=instance.attend_is_longevity,
        attend_is_hare=instance.attend_is_hare,
        attend_note=instance.attend_note,
        attend_nonmember_name=instance.attend_member.member_hash_name)
    new_just_attend.save()


pre_delete.connect(delete_member_attend, sender=EventMemberAttend)
