from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (UserCreationForm, UserChangeForm,
                                       ReadOnlyPasswordHashField)
from django.core import validators
from django.forms import ModelForm, formset_factory, inlineformset_factory
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


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['display_name'].widget.attrs.update(
            {'class': 'form-control'})
        # self.fields['bio'].widget = forms.Textarea(
        #    {'class': 'form-control'})
        self.fields['avatar'].widget.attrs.update(
            {'class': 'form-control'}) # class was formerlly form-control

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
            'placeholder': 'Skill',
            }),
        required=False)


class PositionShortForm(forms.Form):
    """
    Form for user skills
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Position',
            }),
        required=False)
    description = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'placeholder': 'Description',
        })
    )
    pk = forms.IntegerField()



class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = pmodels.Project
        fields = ['name', 'url', 'description', 'requirements', 'time']


class ProjectCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Project Title',
            }),
        required=False
    )
    url = forms.URLField(
        widget=forms.URLInput(attrs={
            'placeholder': 'https://www.example.com',
            }),
        required=False
    )
    description = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'placeholder': 'Description. . . ',
        }),
        required=False
    )
    time = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Time Estimate',
        }),
        required=False
    )
    requirements = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Applicants must be at least 18 years old. . .',
        }),
        required=False
    )
    class Meta:
        model = pmodels.Project
        fields = ['name', 'url', 'description', 'requirements', 'time']



'''
class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['time'].widget.attrs.update(
            {'class': 'form-control'}) # class was formerlly form-control
        self.fields['requirements'].widget.attrs.update(
            {'class': 'form-control'})

    class Meta:
        model = pmodels.Project
        fields = ['name', 'description', 'time', 'requirements']
'''

PositionFormSet = inlineformset_factory(pmodels.Project, pmodels.Position, fields=('name', 'description'))
# prefix = 'positions'
# project = Project.objects.get(name='Foo')
# formset = PositionFormSet(instance=project)


class ProjectQuickForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = pmodels.Project
        fields = ['name', 'url']


# ProjectFormSet = formset_factory(ProjectForm, extra=1)


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


class BasePositionFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two positions have the same name or
        description.
        """
        if any(self.errors):
            return
        return BaseFormSet
        # descriptions = []
        # duplicates = False

        # for form in self.forms:
        #    if form.cleaned_data:
        #        description = form.cleaned_data['description']

                # Check that no two links have the same anchor or URL
        #        if description:
        #            if description in descriptions:
        #                duplicates = True
        #            descriptions.append(description)

        #        if duplicates:
        #            raise forms.ValidationError(
        #                'Positions must have unique descriptions.',
        #                code='duplicate_positions'
        #            )

                # Check that all links have both an anchor and URL


class BaseProjectFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two links have the same anchor or URL
        and that all links have both an anchor and URL.
        """
        if any(self.errors):
            return

        names = []
        urls = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                name = form.cleaned_data['name']
                url = form.cleaned_data['url']

                # Check that no two links have the same anchor or URL
                if name and url:
                    if name in names:
                        duplicates = True
                    names.append(name)

                    if url in urls:
                        duplicates = True
                    urls.append(url)

                if duplicates:
                    raise forms.ValidationError(
                        'Projects must have unique names and URLs.',
                        code='duplicate_links'
                    )

                # Check that all links have both an anchor and URL
                if url and not name:
                    raise forms.ValidationError(
                        'All projects must have a name.',
                        code='missing_name'
                    )
                elif name and not url:
                    raise forms.ValidationError(
                        'All projects must have a URL.',
                        code='missing_URL'
                    )
