from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.models import User
from core.views import MainContentView
from django.template.loader import render_to_string
from django.db import models
from rest_framework import viewsets
from rest_framework import permissions
from .api.serializers import KennelSerializer

from . import models


@login_required
def view_kennel(request, name):
    '''
    Kennel profile
    '''
    # Get kennel
    try:
        kennel = models.Kennel.objects.get(name=name)
    except models.Kennel.DoesNotExist:
        return redirect('kennels')
        # Get user's membership
    my_membership: models.Membership = kennel.memberships.filter(
        user=request.user)
    if my_membership.exists():
        my_membership = my_membership.get()
        active_topbar = kennel.acronym
    else:
        my_membership = None
        active_topbar = 'Kennels'

    base_view = MainContentView(
        template='kennels/kennel.html',
        page_title=kennel.name,
    )
    return base_view.get(
        request=request,
        context={
            'kennel': kennel,
            'my_membership': my_membership,
            'active_sidebar': 'Kennels',
            'active_topbar': active_topbar
        },
    )


# @login_required
# def view_create_kennel(request):
#     '''
#     Kennel creation view
#     '''
#     if request.method == 'POST':
#         f = KennelCreationForm(request.POST)
#         if f.is_valid():
#             kennel: Kennel = f.save()
#             # Add creating user as kennel admin
#             my_membership = kennel.add_member(request.user.member,
#                                               approved=True,
#                                               admin=True)
#             messages.success(request, 'Kennel created successfully')
#             return handle_partial_render(
#                 request, 'kennels/kennel/kennel.html', {
#                     'kennel':
#                     kennel,
#                     'my_membership':
#                     my_membership,
#                     'kennel_membership':
#                     KennelMembership.objects.filter(membership_kennel=kennel),
#                 }, 'kennels/kennels_base.html', kennel.kennel_name)
#     else:
#         f = KennelCreationForm()
#     return handle_partial_render(request, 'kennels/kennel_create.html',
#                                  {'form': f}, 'kennels/kennels_base.html',
#                                  "Create New Kennel")
@login_required
def view_kennels(request):
    '''
    Profile search list
    '''
    base_view = MainContentView(
        template='kennels/kennel_list.html',
        page_title=_('Kennels'),
    )
    return base_view.get(
        request=request,
        context={
            'active_sidebar': 'Kennels',
            'active_topbar': 'Kennels'
        },
    )


# @login_required
# def postMembershipResponse(request):
#     # request should be ajax and method should be POST.
#     if request.accepts("application/json") and request.method == "POST":
#         try:
#             kennel = Kennel.objects.get(kennel_name=request.POST['kennel'])
#         except Kennel.DoesNotExist:
#             return JsonResponse(
#                 {"error": f"Cannot find kennel ({request.POST['kennel']})"},
#                 status=400)
#         try:
#             my_membership = KennelMembership.objects.get(
#                 membership_member=request.user.member,
#                 membership_kennel=kennel)
#             requesting_user = User.objects.get(
#                 username=request.POST["username"])
#             membership_request = KennelMembership.objects.get(
#                 membership_member=requesting_user.member,
#                 membership_kennel=kennel)
#         except KennelMembership.DoesNotExist or User.DoesNotExist:
#             return JsonResponse(
#                 {
#                     "error":
#                     f"Could not find membership request for user ({request.POST['username']}) and kennel ({request.POST['kennel']})"
#                 },
#                 status=400)
#         if not my_membership.membership_is_admin:
#             return JsonResponse(
#                 {
#                     "error":
#                     f"Could not verify admin rights for user ({request.user.username}) and kennel ({kennel.kennel_name})"
#                 },
#                 status=400)
#         if membership_request.membership_is_approved:
#             return JsonResponse(
#                 {
#                     "error":
#                     f"User ({request.user.username}) is already a member of kennel ({kennel.kennel_name})"
#                 },
#                 status=400)
#         if request.POST["choice"] == 'approved':
#             membership_request.membership_is_approved = True
#             membership_request.save()
#         elif request.POST["choice"] == 'denied':
#             membership_request.delete()
#         else:
#             return JsonResponse(
#                 {"error": f'Invalid choice ({request.POST.data["choice"]})'},
#                 status=400)
#         # send to client side.
#         return JsonResponse({}, status=200)
#     # some error occured
#     return JsonResponse({"error": ""}, status=400)

# @login_required
# def postMembershipRequest(request):
#     # request should be ajax and method should be POST.
#     if request.accepts("application/json") and request.method == "POST":
#         try:
#             kennel = Kennel.objects.get(kennel_name=request.POST['kennel'])
#         except Kennel.DoesNotExist:
#             return JsonResponse(
#                 {"error": f"Cannot find kennel ({request.POST['kennel']})"},
#                 status=400)
#         try:
#             my_membership = KennelMembership.objects.get(
#                 membership_member=request.user.member,
#                 membership_kennel=kennel)
#             if my_membership.membership_is_admin:
#                 kennel_admin = KennelMembership.objects.filter(
#                     membership_is_admin=True, membership_kennel=kennel)
#                 if len(kennel_admin) <= 1:
#                     return JsonResponse(
#                         {
#                             "error":
#                             f"You are the last administrator for this kennel ({kennel.kennel_name})"
#                         },
#                         status=400)
#             my_membership.delete()
#         except KennelMembership.DoesNotExist:
#             my_membership = KennelMembership(
#                 membership_member=request.user.member,
#                 membership_kennel=kennel)
#             my_membership.save()
#         # send to client side.
#         return JsonResponse({}, status=200)
#     # some error occured
#     return JsonResponse({"error": ""}, status=400)

# @login_required
# def postConsensus(request):
#     # request should be ajax and method should be POST.
#     if request.accepts("application/json") and request.method == "POST":
#         try:
#             kennel = Kennel.objects.get(id=request.POST['kennel_id'])
#         except Kennel.DoesNotExist:
#             return JsonResponse({"error": f"Cannot find kennel"}, status=400)
#         try:
#             my_membership = KennelMembership.objects.get(
#                 membership_member=request.user.member,
#                 membership_kennel=kennel)
#             if not my_membership.membership_is_admin:
#                 raise KennelMembership.DoesNotExist
#         except KennelMembership.DoesNotExist:
#             return JsonResponse(
#                 {
#                     "error":
#                     f"Could not verify admin rights for user ({request.user.username}) and kennel ({kennel.kennel_name})"
#                 },
#                 status=400)
#         rerenders, appends = [], []
#         if request.POST['type'] == 'kick' or request.POST['type'] == 'admin':
#             try:
#                 consensus_member = Member.objects.get(
#                     id=request.POST["member_id"])
#                 kennel_admin = KennelMembership.objects.filter(
#                     membership_is_admin=True, membership_kennel=kennel)
#                 if len(kennel_admin
#                        ) <= 1 and request.user.member == consensus_member:
#                     return JsonResponse(
#                         {
#                             "error":
#                             f"You are the last administrator for this kennel ({kennel.kennel_name})"
#                         },
#                         status=400)
#             except Member.DoesNotExist:
#                 return JsonResponse(
#                     {
#                         "error":
#                         f"Could not find kennel membership ({kennel.kennel_name})"
#                     },
#                     status=400)
#             if request.POST['type'] == 'kick':
#                 new_consensus = KennelKickConsensus(
#                     consensus_kennel=kennel,
#                     consensus_initiator=request.user.member,
#                     consensus_member=consensus_member)
#             elif request.POST['type'] == 'admin':
#                 try:
#                     membership = KennelMembership.objects.get(
#                         membership_kennel=kennel,
#                         membership_member=consensus_member)
#                 except KennelMembership.DoesNotExist:
#                     return JsonResponse(
#                         {
#                             "error":
#                             f"Could not find membership for user ({consensus_member.member_hash_name}) and kennel ({kennel.kennel_name})"
#                         },
#                         status=400)
#                 new_consensus = KennelAdminConsensus(
#                     consensus_kennel=kennel,
#                     consensus_initiator=request.user.member,
#                     consensus_member=consensus_member,
#                     consensus_action=(not membership.membership_is_admin))
#             new_consensus.save()
#             initiator_vote = KennelConsensusVote(
#                 vote_consensus=new_consensus,
#                 vote_elector=new_consensus.consensus_initiator,
#                 vote=True)
#             initiator_vote.save()
#             if KennelMembership.objects.filter(
#                     membership_kennel=kennel,
#                     membership_is_admin=True).count() > 1:
#                 rerenders.append({
#                     'id':
#                     f'members_{consensus_member.id}_id',
#                     'html':
#                     render_to_string(
#                         'kennels/members/members_search_row.html',
#                         {
#                             "this_member": consensus_member,
#                             "consensus_members": [consensus_member],
#                             "my_membership": my_membership,
#                         },
#                         request,
#                     )
#                 })
#                 appends.append({
#                     'id':
#                     'Current Consensus Votes_table',
#                     'tag':
#                     'tbody',
#                     'html':
#                     render_to_string(
#                         'kennels/consensus/consensus_vote_row.html',
#                         {
#                             'consensus': new_consensus,
#                             'my_vote': initiator_vote
#                         },
#                         request,
#                     )
#                 })
#         # send to client side.
#         return JsonResponse({
#             'rerenders': rerenders,
#             'appends': appends
#         },
#                             status=200)
#     # some error occured
#     return JsonResponse({"error": ""}, status=400)

# @login_required
# def postConsensusVote(request):
#     print(request.POST)
#     if request.accepts("application/json") and request.method == "POST":
#         try:
#             consensus: KennelConsensus = KennelConsensus.objects.get(
#                 id=request.POST['consensus_id'])
#         except KennelConsensus.DoesNotExist:
#             return JsonResponse({"error": f"Cannot find consensus item"},
#                                 status=400)
#         try:
#             my_membership = KennelMembership.objects.get(
#                 membership_member=request.user.member,
#                 membership_kennel=consensus.consensus_kennel)
#             if not my_membership.membership_is_admin:
#                 raise KennelMembership.DoesNotExist
#         except KennelMembership.DoesNotExist:
#             return JsonResponse(
#                 {
#                     "error":
#                     f"Could not verify admin rights for user ({request.user.username}) and kennel ({consensus.consensus_kennel.kennel_name})"
#                 },
#                 status=400)
#         new_vote = KennelConsensusVote(vote_consensus=consensus,
#                                        vote_elector=request.user.member,
#                                        vote=(request.POST['vote'] == 'Yes'))

#         new_vote.save()
#         rerenders = []
#         rerenders.append({
#             'id':
#             f"consensus_{request.POST['consensus_id']}_id",
#             'html':
#             render_to_string(
#                 'kennels/consensus/consensus_vote_row.html',
#                 {
#                     'consensus': consensus,
#                     'my_vote': new_vote
#                 },
#                 request,
#             )
#         })

#         return JsonResponse({
#             'rerenders': rerenders,
#             'appends': []
#         },
#                             status=200)

#     return JsonResponse({"error": ""}, status=400)
