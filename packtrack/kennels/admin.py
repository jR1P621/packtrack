from django.contrib import admin
from . import models


@admin.register(models.Kennel)
class KennelAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'city', 'is_active')
    list_filter = (['is_active'])
    search_fields = ('name', 'acronym', 'city')


@admin.register(models.Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'kennel', 'is_approved', 'is_admin')
    list_filter = ('is_approved', 'is_admin')
    search_fields = ('user', 'kennel')


@admin.register(models.ConsensusVote)
class ConsensusVoteAdmin(admin.ModelAdmin):
    list_display = ('consensus', 'voter', 'vote')
    search_fields = ('consensus', 'voter')


@admin.register(models.Consensus)
class ConsensusAdmin(admin.ModelAdmin):
    list_display = ('initiator', 'kennel', 'membership', 'type')
    list_filter = (['type'])
    search_fields = ('initiator', 'kennel', 'membership')
