from .models import AnchorSet
from django import forms
import re

class AnchorSetForm(forms.ModelForm):
    anchor_set_name = forms.CharField(widget=forms.TextInput({ "placeholder": "use A-Z, a-z, 0-9 and _" }))
    class Meta:
        model = AnchorSet
        fields = ('anchor_set_name', )

    def clean(self):
        cleaned_data = super(AnchorSetForm, self).clean()
        anchor_set_name = cleaned_data.get('anchor_set_name')
        reg = re.compile('^[\w]+$')
        if not reg.match(anchor_set_name):
            raise forms.ValidationError(
                "The anchot set name should only contains characters and numbers"
            )


class RenameAnchorSetForm(forms.Form):
    anchor_set_name = forms.CharField(widget=forms.TextInput({"placeholder": "use A-Z, a-z, 0-9 and _"}))

    def clean(self):
        cleaned_data = super(RenameAnchorSetForm, self).clean()
        anchor_set_name = cleaned_data.get('anchor_set_name')
        reg = re.compile('^[\w]+$')
        if not reg.match(anchor_set_name):
            raise forms.ValidationError(
                "The anchot set name should only contains characters and numbers"
            )


class InputTempoScaleForm(forms.Form):
    tempo_scale = forms.CharField(widget=forms.TextInput({"placeholder": "percentage, ranged from -100 to 100, "
                                                                         "negative value indicates slowing down "
                                                                         "while postive value indicates speeding up"}))

    def clean(self):
        cleaned_data = super(InputTempoScaleForm, self).clean()
        tempo_scale = cleaned_data.get('tempo_scale')
        reg = re.compile('^-?[1-9][0-9]?$|^100$')
        if not reg.match(tempo_scale):
            raise forms.ValidationError(
                "The tempo scale should be percentage ranged from -100 to 100"
            )