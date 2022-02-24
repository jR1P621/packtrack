from django.contrib import admin
from . import models


@admin.register(models.InviteCode)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('invite_code', 'invite_expiration', 'invite_creator',
                    'invite_receiver')