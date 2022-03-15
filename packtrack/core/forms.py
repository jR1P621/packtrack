from django.contrib.auth import forms as auth_forms
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

import datetime, models


class RegistrationForm(forms.Form):
    pass


# class UserCreationInviteForm(auth_forms.UserCreationForm):
#     '''
#     Extends default user creation form to include invite code
#     '''
#     error_messages = {
#         'invalid_invite': _('Invalid Invite Code'),
#     }

#     invitecode = forms.CharField(
#         label=_("Invite Code"),
#         widget=forms.TextInput(attrs={'required': True}),
#         strip=True,
#         help_text=
#         _("Enter a valid invite code. If you don't have one, ask a current member to send you one."
#           ),
#     )
#     invitecode.widget.attrs['class'] = 'form-control'

#     def __init__(self, *args, **kwargs) -> None:
#         super().__init__(*args, **kwargs)
#         for field in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control'

#     def clean_invitecode(self):
#         '''
#         Checks that invite code exists and is not expired or used
#         '''
#         invitecode = self.cleaned_data.get("invitecode")
#         try:
#             invite = models.InviteCode.objects.get(invite_code=invitecode)
#         except models.InviteCode.DoesNotExist:
#             raise ValidationError(
#                 self.error_messages['invalid_invite'],
#                 code='invalid_invite',
#             )
#         else:
#             if invite.invite_receiver or invite.invite_expiration < datetime.date.today(
#             ):
#                 raise ValidationError(
#                     self.error_messages['invalid_invite'],
#                     code='invalid_invite',
#                 )
#         return invitecode

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         try:
#             used_invite: models.InviteCode = models.InviteCode.objects.get(
#                 invite_code=self.cleaned_data.get("invitecode"))
#         except models.InviteCode.DoesNotExist:
#             raise ValidationError(
#                 self.error_messages['invalid_invite'],
#                 code='invalid_invite',
#             )
#         if commit:
#             user.save()
#             used_invite.invite_receiver = user.member
#             used_invite.invite_expiration = None
#             used_invite.save()
#         return user
