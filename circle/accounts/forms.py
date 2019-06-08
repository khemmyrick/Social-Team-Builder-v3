from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (UserCreationForm, UserChangeForm,
                                       ReadOnlyPasswordHashField)
from django.core import validators
from django.forms import ModelForm, formset_factory
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext, ugettext_lazy as _

from django_registration.forms import RegistrationForm

from markdownx.fields import MarkdownxFormField

import pdb

from . import models
from projects import models as pmodels


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


class UserRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = get_user_model()
        fields = ('email', 'username', 'password1', 'password2')


"""
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
    bio = MarkdownxFormField(
        max_length=5000,
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
"""

class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['display_name'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['bio'].widget = forms.Textarea(
            {'class': 'form-control'})

    class Meta:
        model = get_user_model()
        fields = ['display_name', 'bio', 'avatar']


class SkillForm(forms.Form):
    """
    Form for user skills
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            # 'placeholder': 'Link Name / Anchor Text',
            }),
        required=False)


SkillFormset = formset_factory(SkillForm, extra=1)
'''
class SkillForm(ModelForm):
    class Meta:
        model = models.Skill
        fields = ("name",)
'''

'''
SkillFormSet = forms.modelformset_factory(
    model=models.Skill,
    form=SkillForm # form = SkillForm
) # This bit may be "explicitly prohibited."?
'''


'''
# Based on https://medium.com/all-about-django/adding-forms-dynamically-to-a-django-formset-375f1090c2b0
SkillFormSet = forms.modelformset_factory(
    models.Skill,
    fields=('name', ),
    extra=1,
    widgets={'name': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter skill here'
        })
    }
)
'''


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['title'].widget.attrs.update(
        #    {'class': 'form-control'})
        # self.fields['url'].widget.attrs.update(
        #    {'class': 'form-control'})
        # self.fields['description'].widget = forms.Textarea(
        #    {'class': 'form-control'})
        # self.fields['timeline'].widget.attrs.update(
        #    {'class': 'form-control'})
        # self.fields['applicant_requirements'].widget.attrs.update(
        #    {'class': 'form-control'})

    class Meta:
        model = pmodels.Project
        fields = ['name', 'description', 'requirements', 'time']

class BaseSkillFormSet(BaseFormSet):
    def clean(self):
        """Adds validation to check that no two skills have the same text."""
        if any(self.errors):
            return

        names = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                name = form.cleaned_data['name']

                # Check that no two skills have the same text
                if name:
                    if name in names:
                        duplicates = True
                    names.append(name)

                if duplicates:
                    raise forms.ValidationError(
                        "You can't have the same skill twice!",
                        code='duplicate_skills'
                    )
