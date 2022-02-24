from django.contrib import admin
from . import models


@admin.register(models.Kennel)
class KennelAdmin(admin.ModelAdmin):
    list_display = ('kennel_name', 'kennel_abbr', 'kennel_city',
                    'kennel_is_active')
    list_filter = (['kennel_is_active'])
    search_fields = ('kennel_name', 'kennel_abbr', 'kennel_city')


@admin.register(models.KennelMembership)
class KennelMembershipAdmin(admin.ModelAdmin):
    list_display = ('membership_member', 'membership_kennel',
                    'membership_is_approved', 'membership_is_admin')
    list_filter = ('membership_is_approved', 'membership_is_admin')
    search_fields = ('membership_member', 'membership_kennel')
