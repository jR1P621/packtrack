from django.db import models

from members.models import Member
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel

from typing import Tuple

VOTING_MAJORITY = 0.51


class Kennel(models.Model):
    '''
    Kennel model
    '''
    kennel_name = models.CharField(max_length=128, unique=True)
    kennel_abbr = models.CharField(max_length=16, default='')
    kennel_city = models.CharField(max_length=128, null=True)
    kennel_is_active = models.BooleanField(default=True)
    kennel_img = models.ImageField(null=True)
    kennel_about = models.TextField(blank=True, null=True)
    kennel_members = models.ManyToManyField(
        'members.Member',
        through='KennelMembership',
    )
    kennel_events = models.ManyToManyField('events.Event',
                                           through='events.EventHost')
    kennel_longevity_includes = models.ManyToManyField('Kennel')

    def save(self, *args, **kwargs) -> None:
        if self.kennel_abbr == '':
            self.kennel_abbr = 'H3'
        super().save(*args, **kwargs)

    def set_city(self, city: str) -> None:
        self.kennel_city = city

    def add_member(self, member: Member, approved=False, admin=False) -> None:
        new_membership = KennelMembership(membership_member=member,
                                          membership_kennel=self,
                                          membership_is_approved=approved,
                                          membership_is_admin=admin)
        new_membership.save()
        return new_membership

    def __str__(self) -> str:
        return self.kennel_name


class KennelMembership(models.Model):
    '''
    m2m between kennels and members.
    '''
    membership_member = models.ForeignKey('members.Member',
                                          on_delete=models.CASCADE)
    membership_kennel = models.ForeignKey(Kennel, on_delete=models.CASCADE)
    membership_is_approved = models.BooleanField(default=False)
    membership_is_admin = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['membership_member', 'membership_kennel'],
                name='unique_membership_request')
        ]


# Not yet implemented
class KennelURLs(models.Model):
    '''
    STUB. External kennel links.
    '''
    url = models.URLField()
    url_kennel = models.ForeignKey(Kennel, on_delete=models.CASCADE)
    url_desc = models.CharField(max_length=32)


### ADMIN VOTING CONSENSUS ITEMS ###


class KennelConsensus(PolymorphicModel):
    '''
    Base model for admin voting models.
    Certain kennel actions require majority vote of kennel admins.
    '''
    consensus_initiator = models.ForeignKey('members.Member',
                                            on_delete=models.CASCADE)
    consensus_kennel = models.ForeignKey('Kennel', on_delete=models.CASCADE)

    def get_vote_split(self) -> Tuple[float, float]:
        '''
        Gets current Yes/No vote percentages based on total admin pool size.
        '''
        votes = KennelConsensusVote.objects.filter(vote_consensus=self)
        pool_size = KennelMembership.objects.filter(
            membership_kennel=self.consensus_kennel,
            membership_is_admin=True).count()
        yes_percent = votes.filter(vote=True).count() / pool_size
        no_percent = votes.filter(vote=False).count() / pool_size
        return (yes_percent, no_percent)

    def get_readable_votes(self) -> str:
        '''
        Presents current vote splits as a human readable string
        '''
        yes, no = self.get_vote_split()
        return f'Yes: {int(yes*100)}% | No: {int(no*100)}%'

    def perform_action(self) -> None:
        '''
        performs the required consensus action
        '''
        raise NotImplementedError

    def get_desc(self) -> str:
        '''
        Return a human readible string of the consensus instance
        '''
        raise NotImplementedError


class KennelKickConsensus(KennelConsensus):
    '''
    A consensus item to kick a member from the kennel
    '''
    consensus_member = models.ForeignKey('members.Member',
                                         on_delete=models.CASCADE)

    def perform_action(self) -> None:
        '''
        Deletes membership instance iff member is not an admin OR member is not the last admin.
        '''
        try:
            membership: KennelMembership = KennelMembership.objects.get(
                membership_member=self.consensus_member,
                membership_kennel=self.consensus_kennel)
        except KennelMembership.DoesNotExist:
            pass
        else:
            kennel_admin_count = KennelMembership.objects.filter(
                membership_kennel=self.consensus_kennel,
                membership_is_admin=True).count()
            if not membership.membership_is_admin or kennel_admin_count > 1:
                membership.delete()

    def get_desc(self) -> str:
        return f'Kick: {self.consensus_member.member_hash_name}'


class KennelAdminConsensus(KennelConsensus):
    consensus_member = models.ForeignKey('members.Member',
                                         on_delete=models.CASCADE)
    consensus_action = models.BooleanField()

    def perform_action(self) -> None:
        '''
        Adds/removed admin rights for the specified member.
        Does not remove admin rights if the member is the only admin.
        '''
        try:
            membership: KennelMembership = KennelMembership.objects.get(
                membership_member=self.consensus_member,
                membership_kennel=self.consensus_kennel)
        except KennelMembership.DoesNotExist:
            pass
        else:
            kennel_admin_count = KennelMembership.objects.filter(
                membership_kennel=self.consensus_kennel,
                membership_is_admin=True).count()
            if kennel_admin_count > 1 or self.consensus_action:
                membership.membership_is_admin = self.consensus_action
                membership.save()

    def get_desc(self) -> str:
        if self.consensus_action:
            return f'Make Admin: {self.consensus_member.member_hash_name}'
        else:
            return f'Revoke Admin: {self.consensus_member.member_hash_name}'


class KennelDeleteConsensus(KennelConsensus):

    def perform_action(self):
        '''
        Deletes the kennel
        '''
        self.consensus_kennel.delete()


class EventDeleteConsensus(KennelConsensus):
    consensus_event = models.OneToOneField('events.Event',
                                           on_delete=models.CASCADE,
                                           unique=True)


class KennelConsensusVote(models.Model):
    '''
    A vote for a consensus instance
    '''
    vote_consensus = models.ForeignKey('KennelConsensus',
                                       on_delete=models.CASCADE)
    vote_elector = models.ForeignKey('members.Member',
                                     on_delete=models.CASCADE)
    vote = models.BooleanField()

    class Meta:
        # Only allow 1 vote per admin per consensus
        constraints = [
            models.UniqueConstraint(fields=['vote_consensus', 'vote_elector'],
                                    name='unique_consensus_vote')
        ]


@receiver(post_save)
def delete_duplicate(sender, instance, created, **kwargs) -> None:
    '''
    Casts the creating admin's vote as Yes.

    Prevents multiple Kick/Admin consensus instances from being created for the same member per kennel.
    Essentially creates a unique (member,kennel) constraint for these consensus items.
    This is needed due to polymorphic model constraint limitations.
    '''
    if not isinstance(instance, KennelConsensus):
        return
    if created:
        if isinstance(instance, KennelAdminConsensus) or isinstance(
                instance, KennelKickConsensus):
            consensus_type = type(instance)
            consensus_count = consensus_type.objects.filter(
                consensus_kennel=instance.consensus_kennel,
                consensus_member=instance.consensus_member).count()
            if consensus_count > 1:
                instance.delete()
                return
        initiator_vote = KennelConsensusVote(
            vote_consensus=instance,
            vote_elector=instance.consensus_initiator,
            vote=True)
        initiator_vote.save()


@receiver(post_save, sender=KennelConsensusVote)
def check_majority(sender, instance, created, **kwargs) -> None:
    '''
    Checks for majority vote when a vote is cast.
    '''
    if created:
        yes, no = instance.vote_consensus.get_vote_split()
        if yes > VOTING_MAJORITY:
            instance.vote_consensus.perform_action()
            instance.vote_consensus.delete()
        elif no > VOTING_MAJORITY or yes + no == 1:
            instance.vote_consensus.delete()


@receiver(post_delete, sender=KennelMembership)
@receiver(post_delete, sender=KennelAdminConsensus)
def recheck_kennel_consensuses(sender, instance, **kwargs) -> None:
    '''
    Rechecks majority vote for kennel consensus items when an admin is removed.
    '''
    # Admin rights were revoked
    if sender == KennelAdminConsensus and not instance.consensus_action:
        kennel = instance.consensus_kennel
    # Admin left the kennel
    elif sender == KennelMembership and instance.membership_is_admin:
        kennel = instance.membership_kennel
    else:
        return
    kennel_consensuses = KennelConsensus.objects.filter(
        consensus_kennel=kennel)
    for c in kennel_consensuses:
        yes, no = c.get_vote_split()
        if yes > VOTING_MAJORITY:
            c.perform_action()
            c.delete()
        elif no > VOTING_MAJORITY or yes + no == 1:
            c.delete()