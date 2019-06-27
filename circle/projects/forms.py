from django import forms
from django.forms.formsets import BaseFormSet

from projects.models import Project, Position


# to refer to user object use  settings.AUTH_USER_MODEL?
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


class PositionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Position
        fields = ['name', 'description', 'time']

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Position Title',
            }),
        required=True
    )
    description = forms.CharField(
        max_length=60000,
        widget=forms.Textarea(attrs={
            'placeholder': 'Description. . . ',
            }),
        required=True
    )
    time = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': '10 hours/week',
            }),
        required=False
    )


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = ['name', 'url', 'description', 'requirements', 'time']


class ProjectCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Project Title',
            }),
        required=True
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
        required=True
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
        model = Project
        fields = ['name', 'url', 'description', 'requirements', 'time']


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

                # Check that no two skills in one form have the same text
                if name:
                    if name in names:
                        duplicates = True
                    names.append(name)

                if duplicates:
                    raise forms.ValidationError(
                        "You can't have the same skill twice!",
                        code='duplicate_skills'
                    )
