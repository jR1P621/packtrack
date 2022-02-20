from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from . import models
# from models import Member


def view_register(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return HttpResponseRedirect(reverse('login'))

    else:
        f = UserCreationForm()

    return render(request, 'register.html', {'form': f})


@login_required
def view_profile(request):
    return HttpResponse(f"{request.user.username} Profile")


@login_required
def view_dashboard(request):
    try:
        models.Member.objects.get(member_user_account=request.user)
    except models.Member.DoesNotExist:
        new_member = models.Member(member_user_account=request.user,
                                   member_hash_name=request.user.username)
        new_member.save()
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return render(request, 'dashboard.html')