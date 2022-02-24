from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Kennel
from cities_light.models import Country, Region, City
from django.core.exceptions import ValidationError


class KennelCreationForm(forms.ModelForm):
    """
    A form that creates a new kennel with creating user as a kennel administrator
    """

    error_messages = {
        'invalid_city': _("Can't find city"),
    }

    country = forms.ModelChoiceField(queryset=Country.objects.all(),
                                     label=_("Country"),
                                     required=False)
    region = forms.ModelChoiceField(queryset=Region.objects.none(),
                                    label=_("State/Region"),
                                    required=False)
    city = forms.ModelChoiceField(queryset=City.objects.none(),
                                  label=_("City"),
                                  required=True)
    country.widget.attrs['class'] = 'form-control'
    region.widget.attrs['class'] = 'form-control'
    city.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Kennel
        fields = ("kennel_name", 'kennel_abbr', 'kennel_about')
        field_classes = {
            'kennel_name': forms.CharField,
            'kennel_abbr': forms.CharField,
        }
        labels = {'kennel_name': 'Name', 'kennel_abbr': 'Acronym'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.kennel_name in self.fields:
            self.fields[
                self._meta.model.kennel_name].widget.attrs['autofocus'] = True
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['kennel_name'].widget.attrs[
            'placeholder'] = 'Dastardly Drinkers Hash House Harriers'
        self.fields['kennel_abbr'].widget.attrs['placeholder'] = 'D2H3'

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['region'].queryset = Region.objects.filter(
                    country_id=country_id).order_by('name')
                region_id = int(self.data.get('region'))
                self.fields['city'].queryset = City.objects.filter(
                    region_id=region_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk:
            self.fields[
                'region'].queryset = self.instance.country.region_set.order_by(
                    'name')
            self.fields[
                'city'].queryset = self.instance.region.city_set.order_by(
                    'name')

    # def _post_clean(self):
    #     super()._post_clean()

    def save(self, commit=True):
        kennel = super().save(commit=False)
        kennel.set_city(self.cleaned_data["city"])
        if commit:
            kennel.save()
        return kennel