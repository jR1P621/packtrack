from django.contrib.auth import forms as auth_forms
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import InviteCode, Member
from django.core.exceptions import ValidationError
import datetime


class UserCreationInviteForm(auth_forms.UserCreationForm):
    error_messages = {
        'invalid_invite': _('Invalid Invite Code'),
    }

    invitecode = forms.CharField(
        label=_("Invite Code"),
        widget=forms.TextInput(attrs={'required': True}),
        strip=True,
        help_text=
        _("Enter a valid invite code. If you don't have one, ask a current member to send you one."
          ),
    )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def clean_invitecode(self):
        print('check invite')
        invitecode = self.cleaned_data.get("invitecode")
        try:
            invite = InviteCode.objects.get(invite_code=invitecode)
        except InviteCode.DoesNotExist:
            raise ValidationError(
                self.error_messages['invalid_invite'],
                code='invalid_invite',
            )
        else:
            if invite.invite_receiver or invite.invite_expiration < datetime.date.today(
            ):
                raise ValidationError(
                    self.error_messages['invalid_invite'],
                    code='invalid_invite',
                )
        return invitecode

    def save(self, commit=True):
        print('create user')
        user = super().save(commit=False)
        try:
            used_invite: InviteCode = InviteCode.objects.get(
                invite_code=self.cleaned_data.get("invitecode"))
        except InviteCode.DoesNotExist:
            raise ValidationError(
                self.error_messages['invalid_invite'],
                code='invalid_invite',
            )
        if commit:
            user.save()
            used_invite.invite_receiver = user.member
            used_invite.invite_expiration = None
            used_invite.save()
        return user