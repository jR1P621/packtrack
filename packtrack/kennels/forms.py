# from django import forms
# from django.utils.translation import gettext_lazy as _
# from .models import Kennel
# from django.core.exceptions import ValidationError

# class KennelCreationForm(forms.ModelForm):
#     """
#     A form that creates a new kennel with creating user as a kennel administrator
#     """

#     # Used as button for drop down search choice field
#     city = forms.CharField(
#         label='City',
#         required=False,
#         widget=forms.TextInput(attrs={
#             'type': 'button',
#         }),
#     )

#     class Meta:
#         model = Kennel
#         fields = ("kennel_name", 'kennel_abbr', 'kennel_city')
#         field_classes = {
#             'kennel_name': forms.CharField,
#             'kennel_abbr': forms.CharField,
#             'kennel_city': forms.CharField,
#         }
#         labels = {
#             'kennel_name': 'Name',
#             'kennel_abbr': 'Acronym',
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self._meta.model.kennel_name in self.fields:
#             self.fields[
#                 self._meta.model.kennel_name].widget.attrs['autofocus'] = True
#         for field in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control text-left'
#         self.fields['kennel_name'].widget.attrs[
#             'placeholder'] = 'Dastardly Drinkers Hash House Harriers'
#         self.fields['kennel_abbr'].widget.attrs['placeholder'] = 'D2H3'

#     def save(self, commit=True):
#         kennel = super().save(commit=False)
#         if commit:
#             kennel.save()
#         return kennel