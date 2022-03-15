# from django.contrib.auth import forms as auth_forms
# from django import forms
# from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError

# import datetime, models

# class EditProfileForm(forms.ModelForm):
#     '''
#     Allows user to modify parts of their profile
#     '''

#     email = forms.EmailField(
#         label=_("Email"),
#         required=False,
#         # strip=True,
#         help_text=
#         _("Enter a valid invite code. If you don't have one, ask a current member to send you one."
#           ),
#     )

#     class Meta:
#         model = models.Profile
#         fields = ("member_hash_name", 'member_avatar')
#         field_classes = {
#             'member_hash_name': forms.CharField,
#             'member_avatar': forms.ImageField,
#         }
#         labels = {
#             'member_avatar': 'Profile Picture',
#             'member_hash_name': 'Hash Name',
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['member_avatar'].widget = forms.FileInput()
#         for field in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control'
#         self.email.initial = self.Meta.model.member_user_account.email

#     def save(self, commit=True):
#         member = super().save(commit=False)
#         member.member_user_account.email = self.cleaned_data['email']
#         if commit:
#             member.save()
#         return member