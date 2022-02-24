from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Kennel
from django.views.generic import TemplateView
from .forms import KennelCreationForm
from django.contrib import messages
from cities_light.models import Region, City
from django.http import JsonResponse
from django.core import serializers
from typing import Any
from django.db import models


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

    print(f)
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


# class getLinkedElements(TemplateView):
#     template_name = 'helpers/list_options.html'

#     def __init__(self, seed_model: models.Model, linked_model: models.Model,
#                  linked_field: str, **kwargs: Any) -> None:
#         super().__init__(**kwargs)
#         self.seed_model = seed_model
#         self.linked_field = linked_field
#         self.linked_model = linked_model

#     def get(self, request):
#         # request should be ajax and method should be GET.
#         if request.accepts("application/json") and request.method == "GET":
#             seed_id = request.GET.get('seed')
#             results = self.linked_model.objects.filter(
#                 eval(this.linked_field)=seed_id).order_by('name')
#             return render(request, 'helpers/list_options.html',
#                           {'options': results})
#         # some error occured
#         return JsonResponse({"error": ""}, status=400)


@login_required
def getRegions(request):
    # request should be ajax and method should be GET.
    if request.accepts("application/json") and request.method == "GET":
        country_id = request.GET.get('country')
        if country_id == '':
            regions = []
        else:
            regions = Region.objects.filter(
                country_id=country_id).order_by('name')
        return render(request, 'helpers/list_options.html',
                      {'options': regions})
    # some error occured
    return JsonResponse({"error": ""}, status=400)


@login_required
def getCities(request):
    # request should be ajax and method should be GET.
    if request.accepts("application/json") and request.method == "GET":
        region_id = request.GET.get('region')
        if region_id == '':
            cities = []
        else:
            cities = City.objects.filter(region_id=region_id).order_by('name')
        return render(request, 'helpers/list_options.html',
                      {'options': cities})
    # some error occured
    return JsonResponse({"error": ""}, status=400)
