# forms.py
from django import forms
from .models import inscription
from django_countries.fields import CountryField
from location_field.forms.plain import PlainLocationField

class InscriptionForm(forms.ModelForm):
    position_geographique = PlainLocationField(based_fields=['ville'], zoom=7, required=False, widget=forms.TextInput(attrs={'class': 'leaflet-map'}))

    class Meta:
        model = inscription
        fields = ['nom', 'prenom', 'email', 'pays', 'contact', 'ville', 'estclient', 'estinscriptparQR', 'position_geographique']
