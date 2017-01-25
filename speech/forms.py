from .models import AnchorSet
from django import forms

class AnchorSetForm(forms.ModelForm):
    class Meta:
        model = AnchorSet
        fields = ('anchor_set_name', )