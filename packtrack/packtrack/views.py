from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def handle_partial_render(
    request,
    template,
    context,
    base_template,
    page_title='',
):
    print(request.headers)
    if request.accepts(
            "application/json") and 'partial_render' in request.GET.keys():
        return JsonResponse(
            {
                'html': render_to_string(template, context, request=request),
                'pageTitle': f'{_(page_title)} | PackTRAK',
            },
            status=200)
    else:
        return render(
            request, base_template, {
                'right_side': render_to_string(
                    template, context, request=request),
                'page_title': f'{_(page_title)} | PackTRAK'
            })
