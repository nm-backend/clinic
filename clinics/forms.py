from django import forms
from .models import OmsApplication


class OmsApplicationForm(forms.ModelForm):
    class Meta:
        model = OmsApplication
        fields = '__all__'
