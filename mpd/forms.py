from .models import User
from django import forms
import re


class UsernameForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput({"placeholder": "use A-Z, a-z, 0-9 and _"}))
    class Meta:
        model = User
        fields = ('username', )

    def clean(self):
        cleaned_data = super(UsernameForm, self).clean()
        username = cleaned_data.get('username')
        reg = re.compile('^[\w]+$')
        if not reg.match(username):
            raise forms.ValidationError(
                "The anchot set name should only contains characters and numbers"
            )

