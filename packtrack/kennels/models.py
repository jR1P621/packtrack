from django.db import models
from cities_light.models import City


class Kennel(models.Model):
    kennel_name = models.CharField(max_length=128, unique=True)
    kennel_abbr = models.CharField(max_length=16, default='')
    kennel_city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    kennel_is_active = models.BooleanField()
    kennel_img_path = models.ImageField(null=True)
    kennel_about = models.TextField(blank=True)

    # kennel_members = models.ManyToManyField('members.Member',
    #                                         through='KennelMembership')
    # kennel_events = models.ManyToManyField('events.Event',
    #                                        through='events.EventHost')
    # kennel_membership_requests = models.ManyToManyField(
    #     'members.Member', through='members.MembershipRequest')
    def save(self, *args, **kwargs):
        if self.kennel_abbr == '':
            self.kennel_abbr = 'H3'
        super().save(*args, **kwargs)


class KennelMembership(models.Model):
    member_user = models.ForeignKey('members.Member', on_delete=models.CASCADE)
    member_kennel = models.ForeignKey(Kennel, on_delete=models.CASCADE)


class KennelLongevityLink(models.Model):
    longevity_master_kennel = models.ForeignKey(
        Kennel,
        on_delete=models.CASCADE,
        related_name='longevity_master_kennel')
    longevity_linked_kennel = models.ForeignKey(
        Kennel,
        on_delete=models.CASCADE,
        related_name='longevity_linked_kennel')


class KennelURLs(models.Model):
    url = models.URLField()
    url_kennel = models.ForeignKey(Kennel, on_delete=models.CASCADE)
    url_desc = models.CharField(max_length=32)


# create associated member object when user account is created
# @receiver(post_save, sender=Kennel)
# def create_member(sender, instance, created, **kwargs):
#     if created:
#         instance.
