from PIL import Image
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
    """Form to transform user's avatar."""
    # Work in progress.
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = get_user_model()
        fields = ('avatar', 'x', 'y', 'width', 'height')

    def save(self):
        user = super(PhotoForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(user.avatar)
        cropped_image = image.crop((x, y, w+x, h+y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(user.avatar.path)

        return user
