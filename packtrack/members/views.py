import base64
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import UserCreationInviteForm, EditProfileForm
from django.contrib.auth.models import User
from .models import InviteCode, Member
from django.http import JsonResponse
from django.core import serializers
from random import getrandbits
from django.contrib.auth import login

INVITE_CODE_LIMIT = 20


def view_register(request):
    '''
    New user registration page.
    '''
    if request.method == 'POST':
        f = UserCreationInviteForm(request.POST)
        if f.is_valid():
            user = f.save()
            messages.success(request, 'Account created successfully')
            login(request, user)  # log the user in
            return HttpResponseRedirect('/')
    else:
        f = UserCreationInviteForm()

    return render(request, 'register.html', {'form': f})


@login_required
def edit_profile(request):
    '''
    Profile edit page.
    '''
    if request.method == 'POST':
        f = EditProfileForm(request.POST,
                            request.FILES,
                            instance=request.user.member)
        if f.is_valid():
            f.save()
            m = request.user.member
            m.member_avatar = f.cleaned_data['member_avatar']
            m.save()
            print('saved')
            return HttpResponseRedirect(f'/members/{request.user.username}')

    else:
        f = EditProfileForm(None, instance=request.user.member)

    return render(request, 'members/profile/profile_edit.html', {'form': f})


@login_required
def view_profile(request, username):
    '''
    Member Profile
    '''
    try:
        user = User.objects.get(username=username)
        member = Member.objects.get(member_user_account=user)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('members'))
    else:
        return render(request, 'members/profile/profile.html',
                      {'member': member})


@login_required
def view_dashboard(request):
    '''
    Main dashboard
    '''
    try:
        invites = InviteCode.objects.filter(invite_creator=request.user.member)
    except InviteCode.DoesNotExist:
        invites = []
    return render(request, 'dashboard.html', {'invites': invites})


@login_required
def view_members(request):
    '''
    Member search list
    '''
    members = Member.objects.all()
    return render(request, 'members/member_list.html', {'members': members})


@login_required
def postInvite(request):
    '''
    Creates a new InviteCode for the requesting user.
    Invite codes are 48bit random integers encoded with base64 to be 8char strings.
    '''
    # request should be ajax and method should be POST.
    if request.accepts("application/json") and request.method == "POST":
        # only allow a certain number of open invites at a time
        invite_limit = INVITE_CODE_LIMIT
        open_count = InviteCode.objects.filter(
            invite_creator=request.user.member,
            invite_receiver__isnull=True).count()
        if open_count >= invite_limit:
            return JsonResponse(
                {"error": f"Open invites exceeds limit ({invite_limit})"},
                status=400)
        # Generate invite code
        while True:  # Loop if collision (very unlikely)
            new_code_int = getrandbits(48)
            new_code = base64.b64encode(new_code_int.to_bytes(
                6, 'big')).decode("utf-8")
            try:
                InviteCode.objects.get(invite_code=new_code)
            except InviteCode.DoesNotExist:
                break
        # save the data
        new_invite = InviteCode(
            invite_creator=request.user.member,
            invite_code=new_code,
        )
        new_invite.save()
        # serialize in new invite object in json
        ser_invite = serializers.serialize('json', [
            new_invite,
        ])
        # send to client side.
        return JsonResponse({"instance": ser_invite}, status=200)
    # some error occured
    return JsonResponse({"error": ""}, status=400)
