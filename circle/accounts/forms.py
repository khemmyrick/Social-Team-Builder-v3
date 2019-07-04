from django import forms
from django.contrib.auth import get_user_model

from django_registration.forms import RegistrationForm


ROTATE_CHOICES = [
    ('Rotate', (
            ('0', 'No Rotation'),
            ('90', 'Rotate 90 Degrees'),
            ('180', 'Rotate 180 Degrees'),
            ('270', 'Rotate 270 Degrees'),
        )
    ),
    ('Flip', (
            ('vertical', 'Flip Vertical'),
            ('horizontal', 'Flip Horizontal'),
        )
    )
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


class PhotoManipulateForm(forms.ModelForm):
    """Form to transform user's avatar."""
    # Work in progress.
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
    # print('Form variables set.')
    # print('X is {}.  Y is {}. W is {}. H is {}.'.format(x, y, width, height))

    class Meta:
        model = get_user_model()
        fields = ['avatar', 'x', 'y', 'width', 'height']

    def save(self):
        user = super(PhotoManipulateForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(user.avatar)
        cropped_image = image.crop((x, y, w+x, h+y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        resized_image.save(user.avatar.path)
        print('The save function ran.')

        return user


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