from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import Kennel, KennelAdminConsensus, KennelConsensus, KennelConsensusVote, KennelKickConsensus, KennelMembership
from django.views.generic import TemplateView
from .forms import KennelCreationForm
from django.contrib import messages
from django.contrib.auth.models import User


@login_required
def view_kennel(request, kennel_name):
    try:
        kennel = Kennel.objects.get(kennel_name=kennel_name)
    except Kennel.DoesNotExist:
        return HttpResponseRedirect(reverse('kennels'))
    else:
        kennel_membership = KennelMembership.objects.filter(
            membership_kennel=kennel)
        try:
            my_membership: KennelMembership = kennel_membership.get(
                membership_member=request.user.member)
            if my_membership.membership_is_admin:
                consensuses = [{
                    'consensus':
                    c,
                    'my_vote':
                    KennelConsensusVote.objects.filter(
                        vote_consensus=c, vote_elector=request.user.member)
                } for c in KennelConsensus.objects.filter(
                    consensus_kennel=kennel)]
                consensus_members = [
                    c['consensus'].consensus_member for c in consensuses
                ]
                return render(
                    request, 'kennels/kennel/kennel.html', {
                        'kennel': kennel,
                        'my_membership': my_membership,
                        'kennel_membership': kennel_membership,
                        'consensuses': consensuses,
                        'consensus_members': consensus_members
                    })
        except KennelMembership.DoesNotExist:
            my_membership = False
        return render(
            request, 'kennels/kennel/kennel.html', {
                'kennel': kennel,
                'my_membership': my_membership,
                'kennel_membership': kennel_membership,
            })


@login_required
def view_create_kennel(request):
    if request.method == 'POST':
        f = KennelCreationForm(request.POST)
        if f.is_valid():
            kennel: Kennel = f.save()
            kennel.add_member(request.user.member, approved=True, admin=True)
            messages.success(request, 'Kennel created successfully')
            return HttpResponseRedirect(
                f'/kennels/profile/{kennel.kennel_name}')

    else:
        f = KennelCreationForm()

    return render(request, 'kennels/kennel_create.html', {'form': f})


class kennelListView(TemplateView):
    template_name = 'kennels/kennel_list.html'
    user_kennels = False
    kennels = []

    def get(self, request):
        if not self.user_kennels:
            self.kennels = Kennel.objects.all()
            title = 'Kennels'
            color = 'pink'
        else:
            self.kennels = request.user.member.member_kennels.all()
            title = 'My Kennels'
            color = 'white-text green'
        return render(request, self.template_name, {
            'kennels': self.kennels,
            'title': title,
            'color': color
        })


@login_required
def postMembershipResponse(request):
    # request should be ajax and method should be POST.
    if request.accepts("application/json") and request.method == "POST":
        try:
            kennel = Kennel.objects.get(kennel_name=request.POST['kennel'])
        except Kennel.DoesNotExist:
            return JsonResponse(
                {"error": f"Cannot find kennel ({request.POST['kennel']})"},
                status=400)
        try:
            my_membership = KennelMembership.objects.get(
                membership_member=request.user.member,
                membership_kennel=kennel)
            requesting_user = User.objects.get(
                username=request.POST["username"])
            membership_request = KennelMembership.objects.get(
                membership_member=requesting_user.member,
                membership_kennel=kennel)
        except KennelMembership.DoesNotExist or User.DoesNotExist:
            return JsonResponse(
                {
                    "error":
                    f"Could not find membership request for user ({request.POST['username']}) and kennel ({request.POST['kennel']})"
                },
                status=400)
        if not my_membership.membership_is_admin:
            return JsonResponse(
                {
                    "error":
                    f"Could not verify admin rights for user ({request.user.username}) and kennel ({kennel.kennel_name})"
                },
                status=400)
        if membership_request.membership_is_approved:
            return JsonResponse(
                {
                    "error":
                    f"User ({request.user.username}) is already a member of kennel ({kennel.kennel_name})"
                },
                status=400)
        if request.POST["choice"] == 'approved':
            membership_request.membership_is_approved = True
            membership_request.save()
        elif request.POST["choice"] == 'denied':
            membership_request.delete()
        else:
            return JsonResponse(
                {"error": f'Invalid choice ({request.POST.data["choice"]})'},
                status=400)
        # send to client side.
        return JsonResponse({}, status=200)
    # some error occured
    return JsonResponse({"error": ""}, status=400)


@login_required
def postMembershipRequest(request):
    # request should be ajax and method should be POST.
    if request.accepts("application/json") and request.method == "POST":
        try:
            kennel = Kennel.objects.get(kennel_name=request.POST['kennel'])
        except Kennel.DoesNotExist:
            return JsonResponse(
                {"error": f"Cannot find kennel ({request.POST['kennel']})"},
                status=400)
        try:
            my_membership = KennelMembership.objects.get(
                membership_member=request.user.member,
                membership_kennel=kennel)
            if my_membership.membership_is_admin:
                kennel_admin = KennelMembership.objects.filter(
                    membership_is_admin=True, membership_kennel=kennel)
                if len(kennel_admin) <= 1:
                    return JsonResponse(
                        {
                            "error":
                            f"You are the last administrator for this kennel ({kennel.kennel_name})"
                        },
                        status=400)
            my_membership.delete()
        except KennelMembership.DoesNotExist:
            my_membership = KennelMembership(
                membership_member=request.user.member,
                membership_kennel=kennel)
            my_membership.save()
        # send to client side.
        return JsonResponse({}, status=200)
    # some error occured
    return JsonResponse({"error": ""}, status=400)


@login_required
def postConsensus(request):
    # request should be ajax and method should be POST.
    if request.accepts("application/json") and request.method == "POST":
        try:
            kennel = Kennel.objects.get(kennel_name=request.POST['kennel'])
        except Kennel.DoesNotExist:
            return JsonResponse(
                {"error": f"Cannot find kennel ({request.POST['kennel']})"},
                status=400)
        try:
            my_membership = KennelMembership.objects.get(
                membership_member=request.user.member,
                membership_kennel=kennel)
            if not my_membership.membership_is_admin:
                raise KennelMembership.DoesNotExist
        except KennelMembership.DoesNotExist:
            return JsonResponse(
                {
                    "error":
                    f"Could not verify admin rights for user ({request.user.username}) and kennel ({kennel.kennel_name})"
                },
                status=400)
        if request.POST['type'] == 'kick' or request.POST['type'] == 'admin':
            try:
                consensus_user = User.objects.get(
                    username=request.POST["username"])
                kennel_admin = KennelMembership.objects.filter(
                    membership_is_admin=True, membership_kennel=kennel)
                if len(kennel_admin) <= 1 and request.user == consensus_user:
                    return JsonResponse(
                        {
                            "error":
                            f"You are the last administrator for this kennel ({kennel.kennel_name})"
                        },
                        status=400)
            except User.DoesNotExist:
                return JsonResponse(
                    {
                        "error":
                        f"Could not find membership for user ({request.POST['username']}) and kennel ({request.POST['kennel']})"
                    },
                    status=400)
            if request.POST['type'] == 'kick':
                new_consensus = KennelKickConsensus(
                    consensus_kennel=kennel,
                    consensus_initiator=request.user.member,
                    consensus_member=consensus_user.member)
            elif request.POST['type'] == 'admin':
                try:
                    membership = KennelMembership.objects.get(
                        membership_kennel=kennel,
                        membership_member=consensus_user.member)
                except KennelMembership.DoesNotExist:
                    return JsonResponse(
                        {
                            "error":
                            f"Could not find membership for user ({request.POST['username']}) and kennel ({request.POST['kennel']})"
                        },
                        status=400)
                new_consensus = KennelAdminConsensus(
                    consensus_kennel=kennel,
                    consensus_initiator=request.user.member,
                    consensus_member=consensus_user.member,
                    consensus_action=(not membership.membership_is_admin))
                print(new_consensus.consensus_action)
        new_consensus.save()
        # send to client side.
        return JsonResponse({}, status=200)
    # some error occured
    return JsonResponse({"error": ""}, status=400)


@login_required
def postConsensusVote(request):
    if request.accepts("application/json") and request.method == "POST":
        try:
            print(request.POST)
            consensus: KennelConsensus = KennelConsensus.objects.get(
                id=request.POST['consensus_id'])
        except KennelConsensus.DoesNotExist:
            return JsonResponse({"error": f"Cannot find consensus item"},
                                status=400)
        try:
            my_membership = KennelMembership.objects.get(
                membership_member=request.user.member,
                membership_kennel=consensus.consensus_kennel)
            if not my_membership.membership_is_admin:
                raise KennelMembership.DoesNotExist
        except KennelMembership.DoesNotExist:
            return JsonResponse(
                {
                    "error":
                    f"Could not verify admin rights for user ({request.user.username}) and kennel ({consensus.consensus_kennel.kennel_name})"
                },
                status=400)
        new_vote = KennelConsensusVote(vote_consensus=consensus,
                                       vote_elector=request.user.member,
                                       vote=(request.POST['vote'] == 'Yes'))
        new_vote.save()
        return JsonResponse({}, status=200)

    return JsonResponse({"error": ""}, status=400)
