from django.contrib.auth import forms as auth_forms
from django import forms, template
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

import datetime
from . import models


class ImageWidget(forms.widgets.ClearableFileInput):
    template_name = 'widgets/image_field_widget.html'


class EditProfileForm(forms.ModelForm):
    '''
    Allows user to modify parts of their profile
    '''

    email = forms.EmailField(
        label=_("Email"),
        required=False,
    )

    class Meta:
        model = models.Profile
        fields = ("hash_name", 'avatar')
        field_classes = {
            'hash_name': forms.CharField,
            'avatar': forms.ImageField,
        }
        labels = {
            'avatar': '',
            'hash_name': 'Hash Name',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget = ImageWidget()
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.email = self.cleaned_data['email']
        if commit:
            profile.save()
            profile.user.save()
        return profile