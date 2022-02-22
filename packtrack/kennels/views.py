from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Kennel
from django.views.generic import TemplateView


@login_required
def view_kennel(request, kennel_name):
    try:
        kennel = Kennel.objects.get(kennel_name=kennel_name)
    except Kennel.DoesNotExist:
        return HttpResponseRedirect(reverse('kennels'))
    else:
        return render(request, 'kennels/kennel/kennel.html',
                      {'kennel': kennel})


@login_required
def view_kennels(request):
    kennels = Kennel.objects.all()
    return render(request, 'kennels/kennel_search_list.html',
                  {'kennels': kennels})


class kennelListView(TemplateView):
    template_name = 'kennels/kennel_search_list.html'
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
            color = 'green'
        return render(request, 'kennels/kennel_search_list.html', {
            'kennels': self.kennels,
            'title': title,
            'color': color
        })
