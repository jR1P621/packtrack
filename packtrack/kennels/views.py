from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Kennel
from django.views.generic import TemplateView
from .forms import KennelCreationForm
from django.contrib import messages


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
            color = 'white-text green'
        return render(request, self.template_name, {
            'kennels': self.kennels,
            'title': title,
            'color': color
        })
