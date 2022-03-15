from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'host', 'date')
    list_filter = ([])
    search_fields = ('name', 'host', 'date')


@admin.register(models.Attend)
class AttendAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'unclaimed_name', 'event', 'is_hare')
    list_filter = (['is_hare'])
    search_fields = ('user', 'unclaimed_name', 'event')


@admin.register(models.Longevity)
class LongevityAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'kennel')
    list_filter = ([])
    search_fields = ('event', 'kennel')


@admin.register(models.LongevityRecord)
class LongevityRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'attend', 'longevity', 'is_longevity')
    list_filter = ([])
    search_fields = ('attend', 'longevity', 'is_longevity')
