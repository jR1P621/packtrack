from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register(r'kennels', viewsets.KennelViewSet, basename='kennel')
router.register(r'memberships',
                viewsets.MembershipViewSet,
                basename='membership')
router.register(r'consensuses',
                viewsets.ConsensusViewSet,
                basename='consensus')
router.register(r'votes',
                viewsets.ConsensusVoteViewSet,
                basename='consensusvote')
router.register(r'legacy_longevity',
                viewsets.LegacyLongevityViewSet,
                basename='legacylongevity')
