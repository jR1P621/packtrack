from django.contrib import admin
from . import models
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter


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


@admin.register(models.KennelConsensusVote)
class KennelConsensusVoteAdmin(admin.ModelAdmin):
    list_display = ('vote_consensus', 'vote_elector', 'vote')
    search_fields = ('vote_consensus', 'vote_elector')


class KennelConsensusAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = models.KennelConsensus  # Optional, explicitly set here.

    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.
    base_form = ...
    base_fieldsets = (...)


@admin.register(models.KennelAdminConsensus)
class KennelAdminConsensusAdmin(KennelConsensusAdmin):
    base_model = models.KennelAdminConsensus  # Explicitly set here!
    # define custom features here


@admin.register(models.KennelKickConsensus)
class KennelKickConsensusAdmin(KennelConsensusAdmin):
    base_model = models.KennelKickConsensus  # Explicitly set here!
    # define custom features here


@admin.register(models.KennelDeleteConsensus)
class KennelDeleteConsensusAdmin(KennelConsensusAdmin):
    base_model = models.KennelDeleteConsensus  # Explicitly set here!
    # define custom features here


@admin.register(models.EventDeleteConsensus)
class EventDeleteConsensusAdmin(KennelConsensusAdmin):
    base_model = models.EventDeleteConsensus  # Explicitly set here!
    # define custom features here


@admin.register(models.KennelConsensus)
class KennelConsensusParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = models.KennelConsensus  # Optional, explicitly set here.
    child_models = (models.KennelAdminConsensus, models.KennelKickConsensus,
                    models.KennelDeleteConsensus, models.EventDeleteConsensus)
    list_filter = (PolymorphicChildModelFilter, )  # This is optional.
