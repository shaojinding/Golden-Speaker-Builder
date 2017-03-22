from .models import AnchorSet
from django import forms
import re

class AnchorSetForm(forms.ModelForm):
    anchor_set_name = forms.CharField(widget=forms.TextInput({ "placeholder": "use A-Z, a-z and 0-9" }))
    class Meta:
        model = AnchorSet
        fields = ('anchor_set_name', )

    def clean(self):
        cleaned_data = super(AnchorSetForm, self).clean()
        anchor_set_name = cleaned_data.get('anchor_set_name')
        reg = re.compile('[A-Za-z0-9]+')
        if not reg.match(anchor_set_name):
            raise forms.ValidationError(
                "The anchot set name should only contains characters and numbers"
            )
