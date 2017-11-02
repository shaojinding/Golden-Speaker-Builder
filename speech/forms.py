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