from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from core.views import MainContentView
from django.utils.translation import gettext_lazy as _

from . import models, forms

# @login_required
# def edit_profile(request):
#     '''
#     Profile edit page.
#     '''
#     if request.method == 'POST':
#         f = forms.EditProfileForm(
#             request.POST,
#             request.FILES,
#             instance=request.user.profile,
#         )
#         if f.is_valid():
#             profile = f.save()
#             new_avatar = f.cleaned_data['avatar']
#             print(new_avatar)
#             if new_avatar:
#                 profile.avatar = new_avatar
#                 profile.save()
#             return redirect(profile)

#     else:
#         f = forms.EditProfileForm(
#             initial={
#                 'email': request.user.email,
#                 'hash_name': request.user.profile.hash_name,
#             },
#             instance=request.user.profile,
#         )

#     base_view = MainContentView(
#         template='profiles/profile_edit.html',
#         page_title=_('Edit Profile'),
#     )
#     return base_view.get(
#         request=request,
#         context={
#             'form': f,
#             'active_sidebar': 'My Profile',
#             'active_topbar': 'Edit Profile',
#         },
#     )

# @login_required
# def view_profiles(request):
#     '''
#     Profile search list
#     '''
#     base_view = MainContentView(
#         template='profiles/profiles.html',
#         page_title=_('Hashers'),
#     )
#     profiles = models.Profile.objects.all()
#     return base_view.get(
#         request=request,
#         context={
#             'profiles': profiles,
#             'active_sidebar': 'Hashers',
#             'active_topbar': 'Hashers'
#         },
#     )


@login_required
def view_profile(request, username):
    '''
    User Profile
    '''
    try:
        user = User.objects.get(username=username)
        profile = models.Profile.objects.get(user=user)
    except User.DoesNotExist:
        return redirect('hashers')
    base_view = MainContentView(
        template='hashers/profile.html',
        page_title=profile.hash_name,
    )
    if user == request.user:
        active_link = 'My Profile'
    else:
        active_link = 'Hashers'
    return base_view.get(
        request=request,
        context={
            'profile': profile,
            'active_sidebar': active_link,
            'active_topbar': active_link
        },
    )
