from rest_framework import routers

from .viewsets import viewsets

router = routers.DefaultRouter()
router.register(r'users', viewsets.UserViewSet, basename='user')
router.register(r'invite_codes', viewsets.InviteViewSet, basename='invitecode')

# Used so I could create a circular invite code for user #1
# router.register(r'admin_invite_codes',
#                 viewsets.InviteAdminViewSet,
#                 basename='admin_invitecode')
