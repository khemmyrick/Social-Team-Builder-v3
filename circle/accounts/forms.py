from django import forms
from django.contrib.auth import get_user_model

from django_registration.forms import RegistrationForm


ROTATE_CHOICES = [
    ('Rotate', (
            ('0', 'No Rotation'),
            ('90', 'Rotate 90 Degrees'),
            ('180', 'Rotate 180 Degrees'),
            ('270', 'Rotate 270 Degrees'),
    )),
    ('Flip', (
            ('vertical', 'Flip Vertical'),
            ('horizontal', 'Flip Horizontal'),
    ))
]


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


class PhotoEditForm(forms.Form):
    """Form for manipulating user avatars."""
    def __init__(self, *args, **kwargs):
        super(PhotoEditForm, self).__init__(*args, **kwargs)
        self.initial['rotation'] = 'None'
        self.initial['resize'] = 100

    blackwhite = forms.BooleanField(
        help_text="Check to set image to black and white.",
        required=False
    )
    rotation = forms.ChoiceField(
        choices=ROTATE_CHOICES,
        initial="0",
        required=True
    )
    resize = forms.FloatField(
        help_text="Set new image size by percentage from 1-500.",
        max_value=500,
        min_value=1
    )
