from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core import validators

from django_registration.forms import RegistrationForm


"""
class UserCreateForm(MegaBuster, UserCreationForm):
    email = forms.EmailField(max_length=1000, help_text='Required')

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = 'Email Address'
        # def clean(self) would only be needed IF
        # we were comparing 2 or more fields to eachother.
"""


class UserRegistrationForm(RegistrationForm):
    # Used directly in circles/urls for django-registration
    class Meta(RegistrationForm.Meta):
        model = get_user_model()
        fields = ('email', 'username', 'password1', 'password2')


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['display_name'].widget.attrs.update(
            {'class': 'form-control'})
        # self.fields['bio'].widget = forms.Textarea(
        #    {'class': 'form-control'})
        self.fields['avatar'].widget.attrs.update(
            {'class': 'form-control'})  # class was formerlly form-control

    class Meta:
        model = get_user_model()
        fields = ['display_name', 'bio', 'avatar']
