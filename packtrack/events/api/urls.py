from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register(r'events', viewsets.EventViewSet, basename='event')
router.register(r'attendance', viewsets.AttendViewSet, basename='attend')
router.register(r'longevity', viewsets.LongevityViewSet, basename='longevity')
router.register(r'longevityrecords',
                viewsets.LongevityRecordViewSet,
                basename='longevityrecord')
router.register(r'attendclaims',
                viewsets.AttendClaimViewSet,
                basename='attendclaim')
