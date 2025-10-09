from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, US_STATES

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self
        ]))

class CustomUserCreationForm(UserCreationForm):
    # NEW: ask for state (US-only)
    state = forms.ChoiceField(
        choices=US_STATES,
        required=True,
        help_text="Select your US state"
    )

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # keep your original styling
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})
        # style the new state field too
        self.fields['state'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "state")

    def save(self, commit=True):
        # create the user first
        user = super().save(commit=commit)
        # create the one-time profile with state
        state = self.cleaned_data.get("state")
        if commit:
            UserProfile.objects.create(user=user, state=state)
        return user
