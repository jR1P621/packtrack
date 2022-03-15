from django.contrib import admin

from . import models


@admin.register(models.InviteCode)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('code', 'expiration', 'creator', 'receiver')
