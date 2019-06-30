from django import forms
from django.contrib.auth import get_user_model

from django_registration.forms import RegistrationForm


class UserRegistrationForm(RegistrationForm):
    """Form to begin user registration process."""
    class Meta(RegistrationForm.Meta):
        model = get_user_model()
        fields = ('email', 'username', 'password1', 'password2')


class UserForm(forms.ModelForm):
    """Form to update user's account details."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['display_name'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['avatar'].widget.attrs.update(
            {'class': 'form-control'})

    class Meta:
        model = get_user_model()
        fields = ['display_name', 'bio', 'avatar']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['avatar']
