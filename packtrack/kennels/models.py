from django.db import models

from members.models import Member


class Kennel(models.Model):
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

    def save(self, *args, **kwargs):
        if self.kennel_abbr == '':
            self.kennel_abbr = 'H3'
        super().save(*args, **kwargs)

    def set_city(self, city):
        self.kennel_city = city

    def add_member(self, member: Member, approved=False, admin=False):
        new_membership = KennelMembership(membership_member=member,
                                          membership_kennel=self,
                                          membership_is_approved=approved,
                                          membership_is_admin=admin)
        new_membership.save()

    def __str__(self) -> str:
        return self.kennel_name


class KennelMembership(models.Model):
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


class KennelURLs(models.Model):
    url = models.URLField()
    url_kennel = models.ForeignKey(Kennel, on_delete=models.CASCADE)
    url_desc = models.CharField(max_length=32)


# create associated member object when user account is created
# @receiver(post_save, sender=Kennel)
# def create_member(sender, instance, created, **kwargs):
#     if created:
#         instance.
