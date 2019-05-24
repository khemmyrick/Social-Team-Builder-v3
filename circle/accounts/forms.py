from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (UserCreationForm, UserChangeForm,
                                       ReadOnlyPasswordHashField)
from django.core import validators
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext, ugettext_lazy as _

from markdownx.fields import MarkdownxFormField

from . import models


# to refer to user object use  settings.AUTH_USER_MODEL?
class MegaBuster(object):
    """
    Honeypot validator.
    Adds hidden in put field, and verifies that it's empty.
    If not, raise ValidationError.
    """
    megabuster = forms.CharField(required=False,
                                 widget=forms.HiddenInput,
                                 label="DON'T TOUCH",
                                 validators=[validators.MaxLengthValidator(0)]
                                )
    def clean_megabuster(self):
        megabuster = self.cleaned_data['megabuster']
        if len(megabuster) > 0:
            raise forms.ValidationError('Somebody touched!', code='honeypot_violation')
        return megabuster


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


class UserUpdateForm(MegaBuster, UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    display_name = forms.CharField(max_length=140,
                                   initial='',
                                   help_text='Display Name',
                                   widget=forms.TextInput(attrs={
                                        'placeholder': 'PREXISTING DISPLAYNAME HERE',
                                        'class': 'circle--input--h1'
                                        # 'value': '{{ form.display_name.value }}'
                                   }),
                                   required=False)
    # bio = forms.CharField(
    #    max_length=9999999999999999999999999999999999999999999999999999999999,
    #    initial='PREEXISTING BIO HERE',
    #    help_text='Biography',
    #    widget=forms.Textarea(attrs={
    #        'placeholder': 'PREEXISTING BIO HERE'
    #    })
    # )
    bio = MarkdownxFormField(
        max_length=9999999999999999999999999999999999999999999999999999999999,
        initial='PREEXISTING BIO HERE',
        help_text='Biography',
        widget=forms.Textarea(attrs={
            'placeholder': 'PREEXISTING BIO HERE'
        })
    )
    avatar = forms.ImageField(widget=forms.ClearableFileInput(),
                              required=False)
    password = None

    class Meta:
        model = get_user_model()
        fields = ("display_name", "bio", "avatar")


class SkillCreateForm(ModelForm):
    # SELF-DEPRECATION NOTE: Am I using this?
    class Meta:
        model = models.Skill
        exclude = ("name",)


# class SkillForm(forms.Form):
#    """
#    Form for user skills
#    """
#    name = forms.CharField(
#                    max_length=200,
#                    widget=forms.TextInput(attrs={
#                        'placeholder': 'Skill Type',
#                    }),
#                    required=False)

class SkillForm(ModelForm):
    class Meta:
        model = models.Skill
        fields = ("name",)


SkillFormSet = forms.modelformset_factory(
    model=models.Skill,
    form=SkillForm # form = SkillForm
) # This bit may be "explicitly prohibited."?


class BaseSkillFormSet(BaseFormSet):
    # SELF-DEPRECATION NOTE: Am I using this?
    def clean(self):
        """
        Adds validation to check that no two skills have the same name
        and that all skills have a name.
        """
        if any(self.errors):
            return

        names = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                name = form.cleaned_data['name']

                # Check that no two skills have the same name
                if name:
                    if name in names:
                        duplicates = True
                    names.append(name)

                if duplicates:
                    raise forms.ValidationError(
                        'Skills must have unique names.',
                        code='duplicate_names'
                    )
