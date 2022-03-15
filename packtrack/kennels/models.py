from django.db import IntegrityError, models
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.db.models import Q
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from typing import Tuple

from events.models import Longevity

from .settings import VOTING_MAJORITY, CONSENSUS_TYPES


class Kennel(models.Model):
    '''
    Kennel model
    '''
    name = models.CharField(max_length=128, unique=True)
    acronym = models.CharField(max_length=16)
    city = models.CharField(max_length=128, null=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(null=True)
    about = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User,
                                     through='Membership',
                                     related_name='kennels')

    # events = models.ManyToManyField('events.Event', through='events.Host')

    def __str__(self) -> str:
        return self.name

    def get_kennel_admins(self):
        return User.objects.filter(memberships__kennel=self,
                                   memberships__is_admin=True)


class Membership(models.Model):
    '''
    m2m between kennels and members.
    '''
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='memberships')
    kennel = models.ForeignKey(Kennel,
                               on_delete=models.CASCADE,
                               related_name='memberships')
    is_approved = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'kennel'],
                                    name='unique_membership')
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.kennel}"


# # Not yet implemented
# class KennelURLs(models.Model):
#     '''
#     STUB. External kennel links.
#     '''
#     url = models.URLField()
#     kennel = models.ForeignKey(Kennel, on_delete=models.CASCADE)
#     desc = models.CharField(max_length=32)

### ADMIN VOTING CONSENSUS ITEMS ###


class Consensus(models.Model):
    '''
    Base model for admin voting models.
    Certain kennel actions require majority vote of kennel admins.
    '''
    initiator = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name='initiated_consensuses')
    kennel = models.ForeignKey('Kennel', on_delete=models.CASCADE)
    type = models.IntegerField()
    membership = models.ForeignKey(Membership,
                                   null=True,
                                   on_delete=models.CASCADE,
                                   related_name='consensus')
    event = models.ForeignKey('events.Event',
                              null=True,
                              on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(membership__isnull=False,
                                           event__isnull=True,
                                           type__in=[0, 1, 2])
                                   | Q(membership__isnull=True,
                                       event__isnull=False,
                                       type__in=[3, 4]),
                                   name='consensus_type_constraint'),
            models.UniqueConstraint(fields=['kennel', 'membership'],
                                    name='unique_membership_consensus'),
            models.UniqueConstraint(fields=['kennel', 'event'],
                                    name='unique_event_consensus'),
        ]

    def get_split(self) -> Tuple[float, float]:
        '''
        Gets current Yes/No vote percentages based on total admin pool size.
        '''
        votes = ConsensusVote.objects.filter(consensus=self)
        pool_size = votes.count()
        yes_percent = votes.filter(vote=True).count() / pool_size
        no_percent = votes.filter(vote=False).count() / pool_size
        return (yes_percent, no_percent)

    def get_readable_votes(self) -> str:
        '''
        Presents current vote splits as a human readable string
        '''
        yes, no = self.get_split()
        return _(f'Yes: {int(yes*100)}% | No: {int(no*100)}%')

    def perform_action(self) -> None:
        '''
        performs the required consensus action
        '''
        # Perform action based on type
        # kick member
        if self.type == 0:
            if self.membership.is_admin and not self.kennel.get_kennel_admins(
            ).count() > 1:
                pass
                # "NONE (cannot kick last admin)"
            else:
                self.membership.delete()
        # make admin
        elif self.type == 1:
            self.membership.is_admin = True
            self.membership.save()
        # revoke admin
        elif self.type == 2:
            if self.kennel.get_kennel_admins().count() > 1:
                self.membership.is_admin = False
                self.membership.save()
                # recheck all consensus majority votes
                c: Consensus
                for c in Consensus.objects.filter(kennel=self.kennel):
                    if c != self:
                        c.check_for_majority()
            else:
                pass
                # "NONE (cannot revoke last admin)"
        # add event longevity
        elif self.type == 3:
            Longevity.objects.create(kennel=self.kennel, event=self.event)
        # remove event longevity
        elif self.type == 4:
            Longevity.objects.filter(kennel=self.kennel,
                                     event=self.event).delete()

    def get_desc(self) -> str:
        '''
        Return a human readible string of the consensus instance
        '''
        if self.type == 0:  #kick
            return f"{_('Kick:')} {self.membership.user.profile.hash_name}"
        elif self.type == 1:  # make admin
            return f"{_('Make Admin:')} {self.membership.user.profile.hash_name}"
        elif self.type == 2:  # revoke admin
            return f"{_('Revoke Admin:')} {self.membership.user.profile.hash_name}"
        elif self.type == 3:  # add longevity
            return f"{_('Add Longevity:')} {self.event}"
        elif self.type == 4:  # revoke admin
            return f"{_('Remove Longevity:')} {self.event}"

    def check_for_majority(self):
        yes, no = self.get_split()
        print([yes, no])
        if yes > VOTING_MAJORITY:
            self.perform_action()
        elif no > VOTING_MAJORITY or yes + no == 1:
            pass
            # "NONE (no majority vote)"
        else:
            return
        self.delete()

    def __str__(self) -> str:
        return self.get_desc()


class ConsensusVote(models.Model):
    '''
    A vote for a consensus instance
    '''
    consensus = models.ForeignKey('Consensus', on_delete=models.CASCADE)
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.BooleanField(null=True)

    class Meta:
        # Only allow 1 vote per admin per consensus
        constraints = [
            models.UniqueConstraint(fields=['consensus', 'voter'],
                                    name='unique_vote')
        ]

    def __str__(self) -> str:
        return f"{self.voter} - {self.consensus}"


class LegacyLongevity(models.Model):
    '''
    Allows manual entry of unrecorded attendance
    '''
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='legacy_longevity')
    kennel = models.ForeignKey(Kennel,
                               on_delete=models.CASCADE,
                               related_name='legacy_longevity')
    count = models.PositiveSmallIntegerField()
    hares = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'kennel'],
                                    name='unique_legacy_longevity')
        ]


### SIGNALS ###

# Membership


@receiver(post_delete, sender=Membership)
def recheck_consensuses(sender, instance, **kwargs) -> None:
    '''
    Rechecks majority vote for all kennel consensus items when an admin is removed.
    Deletes remaining consensuses initiated by the removed admin
    '''
    if instance.is_admin:
        c: Consensus
        for c in Consensus.objects.filter(kennel=instance.kennel):
            if c.initiator == instance.user:
                c.delete()
            else:
                c.check_for_majority()


# Consensus


@receiver(pre_save, sender=Consensus)
def verify_consensus_integrity(sender, instance, **kwargs) -> None:
    '''
    Ensures creator/editor has admin membership
    Extra constraint checks
    '''
    if not instance.initiator in instance.kennel.get_kennel_admins():
        raise PermissionError
    if instance.type == 1 and instance.membership.is_admin:
        raise IntegrityError
    if instance.type == 2 and not instance.membership.is_admin:
        raise IntegrityError
    if instance.type == 3 and instance.kennel in instance.event.kennels.all():
        raise IntegrityError
    if instance.type == 4 and instance.kennel not in instance.event.kennels.all(
    ):
        raise IntegrityError


@receiver(post_save, sender=Consensus)
def cast_initiator_vote(sender, instance, created, **kwargs) -> None:
    '''
    Creates empty vote objects for all kennel admins
    Casts a YES vote for the consensus initiator
    '''
    if created:
        ConsensusVote.objects.bulk_create([
            ConsensusVote(consensus=instance, voter=a)
            for a in instance.kennel.get_kennel_admins()
        ])
        initiator_vote = ConsensusVote.objects.get(consensus=instance,
                                                   voter=instance.initiator)
        initiator_vote.vote = True
        initiator_vote.save()


# Vote


@receiver(pre_save, sender=ConsensusVote)
def verify_consensus_vote_integrity(sender, instance, **kwargs) -> None:
    '''
    Ensure voter has kennel admin rights
    '''
    if not instance.voter in instance.consensus.kennel.get_kennel_admins():
        consensus = instance.consensus
        instance.delete()
        consensus.check_for_majority()
        raise PermissionError


@receiver(post_save, sender=ConsensusVote)
def check_majority(sender, instance, created, **kwargs) -> None:
    '''
    Checks for majority vote when a vote is cast.
    '''
    instance.consensus.check_for_majority()
