from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm


def view_register(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return HttpResponseRedirect(reverse('register'))

    else:
        f = UserCreationForm()

    return render(request, 'register.html', {'form': f})


@login_required
def view_profile(request):
    return HttpResponse("hello")