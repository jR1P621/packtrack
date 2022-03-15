from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

# def handle_partial_render(
#     request,
#     template,
#     context,
#     base_template,
#     page_title='',
# ):
#     # print(request.headers)
#     if request.accepts(
#             "application/json") and 'partial_render' in request.GET.keys():
#         return JsonResponse(
#             {
#                 'html': render_to_string(template, context, request=request),
#                 'page_title': f'{_(page_title)} | PackTRAK',
#             },
#             status=200)
#     else:
#         return render(
#             request, base_template, {
#                 'content': render_to_string(template, context,
#                                             request=request),
#                 'page_title': f'{_(page_title)} | PackTRAK'
#             })


class MainContentView(TemplateView):
    '''
    '''

    def __init__(self, template=None, page_title='', **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_template = 'base.html'
        self.template = template
        self.page_title = page_title

    def get(self, request, context: dict):
        if request.accepts(
                "application/json") and 'partial_render' in request.GET.keys():
            return JsonResponse(
                {
                    'html':
                    render_to_string(self.template, context, request=request),
                    'page_title':
                    f'{_(self.page_title)} | PackTRAK',
                },
                status=200)
        else:
            return render(
                request, self.base_template, {
                    'content':
                    render_to_string(self.template, context, request=request),
                    'page_title':
                    f'{_(self.page_title)} | PackTRAK'
                })


# def view_register(request):
#     '''
#     New user registration page.
#     '''
#     if request.method == 'POST':
#         f = forms.UserCreationInviteForm(request.POST)
#         if f.is_valid():
#             user = f.save()
#             messages.success(request, 'Account created successfully')
#             login(request, user)  # log the user in
#             return redirect('dashboard')
#     else:
#         f = forms.UserCreationInviteForm()

#     return render(request, 'register.html', {'form': f})


@login_required
def view_dashboard(request):
    '''
    Main dashboard
    '''
    base_view = MainContentView('core/dashboard.html', 'Dashboard')

    return base_view.get(request, {
        'active_sidebar': 'Dashboard',
    })
