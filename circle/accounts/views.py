from django.conf import settings
# Custom user is in settings import?
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.forms import inlineformset_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from django_registration.views import ActivationView

from rest_framework import generics, permissions, status
from rest_framework.response import Response

import pdb

from . import forms
from accounts.models import User, Skill
from projects.models import Project, Applicant


# Create your views here.
'''
class ActivateView(ActivationView):
    def activate(*args, **kwargs):
'''


@login_required
def profile_update_view(request, pk):
    user = User.objects.get(id=pk)
    session_user = request.user
    # 1. Make sure user is editing their own details.
    if session_user.id != user.id:
        messages.error(
            request,
            "You must be logged in as {} to do that!".format(user.username)
        )
        return HttpResponseRedirect(reverse('home'))
    # 2. Create formset.
    SkillFormset = inlineformset_factory(User, Skill, fields=('name',))
    if request.method == 'POST':
        formset = SkillFormset(request.POST, instance=user)
        if formset.is_valid():
            formset.save()
            return redirect('accounts:details', pk=pk)
            

    formset = SkillFormset(instance=user)
    context = {
        # 'form': form,
        'formset': formset,
    }
    return render(request, 'accounts/user_form.html', context)
'''
@login_required
def profile_update_view(request, pk):
    session_user = request.user
    user = User.objects.get(id=pk)
    userdata = {
        'display_name': user.display_name,
        'bio': user.bio
    }
    if session_user.id != user.id:
        messages.error(
            request,
            "You must be logged in as {} to do this.".format(user.username)
        )
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'GET':
        print("Request is get.")
        form = forms.UserUpdateForm(initial=userdata, prefix='userform')
        print("User form is created.")
        formset = forms.SkillFormSet(queryset=user.skills.all(), prefix='skillset')
        # GOTO CONTEXT LINE...
    elif request.method == 'POST':
        pdb.set_trace()
        form = forms.UserUpdateForm(request.POST, prefix='userform')
        formset = forms.SkillFormSet(request.POST, prefix='skillset')
        if form.is_valid() and formset.is_valid():
            user = form.save(update_fields=['display_name', 'bio']) # update_fields=['display_name', 'bio']
            for skillform in formset:
                skill = skillform.save(commit=False)
                user.skills.add(skill)
                skill.save()
                user.save()
            return redirect('accounts:details', pk=pk)

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'accounts/user_form.html', context)
'''
"""
@login_required
def profile_update_view(request, pk):
    session_user = request.user
    user = User.objects.get(id=pk)
    userdata = {
        'display_name': user.display_name,
        'bio': user.bio,
    }
    if session_user.id != user.id:
        messages.error(request,
                       "You must be logged in as THAT USER to do this.")
        return HttpResponseRedirect(reverse('home'))

    extra_forms = 2
    formset = forms.SkillFormSet(queryset=user.skills.all(), prefix="skillset")
    user_skills = user.skills.order_by('name')
    skill_data = [{'name': skill.name} for skill in user_skills]
    if request.method == 'POST':
        pdb.set_trace()
        if 'additems' in request.POST and request.POST['additems'] == 'true':
            formset_dict_copy = request.POST.copy()
            print(formset_dict_copy)
            # https://stackoverflow.com/questions/5895588/django-multivaluedictkeyerror-error-how-do-i-deal-with-it
            # use MultiValueDict get method?
            formset_dict_copy['skillset-TOTAL_FORMS'] = int(
                formset_dict_copy['skillset-TOTAL_FORMS']
            ) + extra_forms
            form = forms.UserUpdateForm(request.POST, request.FILES)
            formset = forms.SkillFormSet(formset_dict_copy)
        else:
            formset = forms.SkillFormSet(request.POST)
        if form.is_valid() and formset.is_valid(): # Now we get management form missing or tampered with error on formset.
            if form.cleaned_data['display_name']:
                user.display_name = form.cleaned_data['display_name']
                print("6. We got a display name!")
            if form.cleaned_data['bio']:
                user.bio = form.cleaned_data['bio']
                print("7. We got a bio!")
            if form.cleaned_data['avatar']:
                user.avatar = form.cleaned_data['avatar']
                print("8. We got an avatar.")
            user.save()
            print("This user should be in the database.")
            # Now save the data for each form in the formset
            new_skills = []

            for skill_form in formset:
                # name = skill_form.cleaned_data.get('name')
                # if skill_form.cleaned_data['name']:
                name = skill_form.cleaned_data.get('name')
                print("We got a cleaned name: {}".format(name))
                if name:
                    skill, _ = Skill.objects.get_or_create(name=name)
                    print("Getting or creating {}".format(skill.name))
                    skill.save()
                    print("Saving {}".format(skill.name))
                    new_skills.append(skill)
                    # Prepare to instantiate skills without m2m values.
                    # Must save instances first.
            try:
                # print("Entering atomic block.")
                # with transaction.atomic():
                    # "Delete" existing skills.
                for skill in skill_data:
                    user.skills.remove(
                        Skill.objects.get(
                            name=skill['name']
                        ).id
                    )
                    # More lines fewer variables? Or more variables fewer lines?
                    # obj = Skill.objects.get(name=skill['name'])
                    # user.skills.remove(obj.id)
                # Create new skills.
                user.save()
                for skill in new_skills:
                    skill.save()
                    print("Creating/opening. {}".format(skill.name))
                    user.skills.add(skill.id)
                    user.save()
                    # Using add() on a relation that already exists won’t duplicate the relation,
                    print("Added {} to {}'s skills.".format(
                        skill.name, user.display_name
                    ))
                user.save()

            except IntegrityError: #If the transaction failed
                messages.error(request, 'There was an error saving your profile.')
                print("There was an error saving your profile.")
                # Should this be reloading the edit template????
                return HttpResponseRedirect(reverse('accounts:details', pk=pk))

            messages.success(request, 'You have updated your profile!')
            return HttpResponseRedirect(reverse('home'))

        else:
            print(form.errors)
            print("Profile form is INVALID.")
            messages.error(request, 'Invalid form!')
            return HttpResponseRedirect(reverse('home'))
    else:
        # Else if request == get
        print("Request is get.")
        form = forms.UserUpdateForm(initial=userdata)
        print("User form is created.")
        formset = forms.SkillFormSet(queryset=user.skills.all(), prefix='skillset')
        # formset = forms.SkillFormSet(initial=skill_data, prefix='skillset')
        # commented out code above loaded ALL skills?
        # formset = SkillFormSet(initial=skill_data)

    context = {
        'form': form,
        'formset': formset,
    }
    print("4. Context is created.")
    return render(request, 'accounts/user_form.html', context)
"""

"""
@login_required
def profile_update_view(request, pk):
    '''
    Allows a user to update their own profile.
    Skill form functionality not included.
    '''
    session_user = request.user
    print("1. Getting user object.")
    user = User.objects.get(id=pk)
    userdata = {
        'display_name': user.display_name,
        'bio': user.bio,
    }
    # PASS USERDATA A DICT FOR INITIAL DATA
    # formset = ''
    # Make sure we're logged in as user editing this profile.
    if session_user.id == user.id:
        print('2. {} is indeed {}'.format(user.display_name,
                                       session_user.display_name))
        formset = forms.SkillFormSet(queryset=user.skills.all(), prefix="skillset")
        print("2.5 Skill Formset factory should be created.")
        # Get our initial skill data for this user.
        user_skills = user.skills.order_by('name')
        skill_data = [{'name': skill.name} for skill in user_skills]
        if request.method == 'POST':
            print("3. Request method is post.")
            form = forms.UserUpdateForm(request.POST, request.FILES)
            # form = forms.UserUpdateForm(request.POST, request.FILES, instance=user)
            # form needs instance, else it makes new instance??
            # We aren't getting the new form data yet?
            print("4. form should be created.")
            formset = forms.SkillFormSet(request.POST, queryset=user.skills.all(), prefix='skillset')
            print("4.5 formset should be created.")

            if form.is_valid() and formset.is_valid():
                print("5. Profile form and skill formset are valid!")
                # Save user info
                # user.display_name = form.cleaned_data.get('display_name')
                if form.cleaned_data['display_name']:
                    user.display_name = form.cleaned_data['display_name']
                    print("6. We got a display name!")
                # user.bio = form.cleaned_data.get('bio')
                if form.cleaned_data['bio']:
                    user.bio = form.cleaned_data['bio']
                    print("7. We got a bio!")
                # user.avatar = form.cleaned_data.get('avatar')
                if form.cleaned_data['avatar']:
                    user.avatar = form.cleaned_data['avatar']
                    print("8. We got an avatar.")
                user.save()
                print("This user should be in the database.")
                
                # Now save the data for each form in the formset
                new_skills = []

                for skill_form in formset:
                    # name = skill_form.cleaned_data.get('name')
                    # if skill_form.cleaned_data['name']:
                    name = skill_form.cleaned_data.get('name')
                    print("We got a cleaned name: {}".format(name))
                    if name:
                        skill, _ = Skill.objects.get_or_create(name=name)
                        print("Getting or creating {}".format(skill.name))
                        skill.save()
                        print("Saving {}".format(skill.name))
                        new_skills.append(skill)
                        # Prepare to instantiate skills without m2m values.
                        # Must save instances first.

                try:
                    # print("Entering atomic block.")
                    # with transaction.atomic():
                        # "Delete" existing skills.
                    for skill in skill_data:
                        user.skills.remove(
                            Skill.objects.get(
                                name=skill['name']
                            ).id
                        )
                        # More lines fewer variables? Or more variables fewer lines?
                        # obj = Skill.objects.get(name=skill['name'])
                        # user.skills.remove(obj.id)
                    # Create new skills.
                    user.save()
                    for skill in new_skills:
                        skill.save()
                        print("Creating/opening. {}".format(skill.name))
                        user.skills.add(skill.id)
                        user.save()
                        # Using add() on a relation that already exists won’t duplicate the relation,
                        print("Added {} to {}'s skills.".format(
                            skill.name, user.display_name
                        ))
                    user.save()

                except IntegrityError: #If the transaction failed
                    messages.error(request, 'There was an error saving your profile.')
                    print("There was an error saving your profile.")
                    # Should this be reloading the edit template????
                    return HttpResponseRedirect(reverse('accounts:details', pk=pk))

                # And notify our users that it worked
                messages.success(request, 'You have updated your profile!')
                print("You have updated your profile.")
                return HttpResponseRedirect(reverse('home'))

            else:
                print(form.errors)
                print("Profile form is INVALID.")
                messages.error(request, 'Invalid form!')
                return HttpResponseRedirect(reverse('home'))

        else:
            # Else if request == get
            print("Request is get.")
            form = forms.UserUpdateForm(initial=userdata)
            print("User form is created.")
            formset = forms.SkillFormSet(queryset=user.skills.all(), prefix='skillset')
            # formset = forms.SkillFormSet(initial=skill_data, prefix='skillset')
            # commented out code above loaded ALL skills.
            # formset = SkillFormSet(initial=skill_data)

    context = {
        'form': form,
        'formset': formset,
    }
    print("4. Context is created.")
    # Is this the initial load of the edit template?

    return render(request, 'accounts/user_form.html', context)
"""


"""
@login_required
def profile_update_view(request, pk):
    '''
    Allows a user to update their own profile.
    '''
    session_user = request.user
    print("1. Getting user object.")
    user = User.objects.get(id=pk)

    # Create the formset, specifying the form and formset we want to use.
    # SkillFormSet = formset_factory(forms.SkillForm, formset=forms.BaseSkillFormSet)
    SkillFormSet = forms.SkillFormSet(queryset=user.skills.all(), prefix="skillset")
    print("2. Skill Formset factory should be created.")

    # Get our existing skill data for this user.  This is used as initial data.
    user_skills = user.skills.order_by('name')
    skill_data = [{'name': skill.name} for skill in user_skills]

    print("3. Getting existing user skill data. In total: {}".format(len(user_skills)))
    # Make sure we're logged in as user editing this profile.
    if session_user.id == user.id:
        print('{} is indeed {}'.format(user.display_name,
                                       session_user.display_name))
        if request.method == 'POST':
            print("4. Request method is post.")
            form = forms.UserUpdateForm(request.POST, request.FILES)
            # form = forms.UserUpdateForm(request.POST, request.FILES, instance=user)
            # form needs instance, else it makes new instance.
            # We aren't getting the new form data yet?
            print("5. form should be created.")
            # formset = SkillFormSet(request.POST)
            formset = forms.SkillFormSet(request.POST, prefix='skillset')
            print("6. formset created.")

            if form.is_valid() and formset.is_valid():
                # Why isn't my form valid?
                print("Profile form and skill formset are valid!")
                # Save user info
                # user.display_name = form.cleaned_data.get('display_name')
                user.display_name = form.cleaned_data['display_name']
                print("We got a display name!")
                # user.bio = form.cleaned_data.get('bio')
                user.bio = form.cleaned_data['bio']
                print("We got a bio!")
                # user.avatar = form.cleaned_data.get('avatar')
                user.avatar = form.cleaned_data['avatar']
                print("We even got an avatar.")
                user.save()
                print("This user should be in the database.")

                # Now save the data for each form in the formset
                new_skills = []

                for skill_form in formset:
                    # name = skill_form.cleaned_data.get('name')
                    name = skill_form.cleaned_date['name']
                    if name:
                        skill, _ = Skill.objects.get_or_create(name=name)
                        print("Getting or creating {}".format(skill.name))
                        new_skills.append(skill)
                        # Prepare to instantiate skills without m2m values.
                        # Must save instances first.

                try:
                    print("Entering atomic block.")
                    with transaction.atomic():
                        # Delete existing skills.
                        for skill in skill_data:
                            user.skills.remove(
                                Skill.objects.get(
                                    name=skill['name']
                                ).id
                            )
                            # More lines fewer variables? Or more variables fewer lines?
                            # obj = Skill.objects.get(name=skill['name'])
                            # user.skills.remove(obj.id)
                        # Create new skills.
                        for skill in new_skills:
                            skill.save()
                            print("Creating/opening. {}".format(skill.name))
                            user.skills.add(skill.id)
                            # Using add() on a relation that already exists won’t duplicate the relation,
                            print("Added {} to {}'s skills.".format(
                                skill.name, user.display_name
                            ))
                        # And notify our users that it worked
                        messages.success(request, 'You have updated your profile!')
                        print("You have updated your profile.")

                except IntegrityError: #If the transaction failed
                    messages.error(request, 'There was an error saving your profile.')
                    print("There was an error saving your profile.")
                    # Should this be reloading the edit template????
                    return HttpResponseRedirect(reverse('accounts:details', pk=pk))
            else:
                print("Profile form is invalid.")
                messages.error(request, 'Invalid form!')
                return HttpResponseRedirect(reverse('accounts:details', pk=pk))

        else:
            print("1. Else block runs when template is first loaded?")
            print("This is the initial load.")
            # form = forms.UserUpdateForm(user=user)
            form = forms.UserUpdateForm()
            print("2. user form is created.")
            # unexpected keyword argument 'user'
            # For your Initial data loading near the bottom
            formset = forms.SkillFormSet(initial=skill_data, prefix='skillset')
            # formset = SkillFormSet(initial=skill_data)
            print("3. skill formset is created.")

    context = {
        'form': form,
        'formset': formset,
    }
    print("4. Context is created.")
    # Is this the initial load of the edit template?

    return render(request, 'accounts/user_form.html', context)
    # User form context working.
    # Adjust skill formset context next.
"""


def profile_detail_view(request, pk):
    """
    Allows a user to update their own profile.
    """
    user = request.user
    print("1. Session user object.")
    target_user = User.objects.get(id=pk)
    print("2. Getting profile user.")
    # user_skills = user.skills.order_by('name')
    # print("Geting skill data for target user.")
    context = {
        'user': user,
        'target_user': target_user,
    }
    print("3. Context is created.")
    # Is this the initial load of the edit template?

    return render(request, 'accounts/user_detail.html', context)


class LogInView(generic.FormView):
    form_class = AuthenticationForm
    success_url = reverse_lazy("home")
    # success_url should point to page which displays
    # 1. all projects loggedin user created
    # 2. a list of projects that need user's skill set.
    template_name = "accounts/signin.html"

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request, **self.get_form_kwargs())

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class LogOutView(generic.RedirectView):
    url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class SignUpView(generic.CreateView):
    # Model handled in form.
    permission_classes = (permissions.AllowAny,)
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'
    # For EXCEEDS initiate email validation here.
    # 1. create user as inactive by default.
    # 2. "email" user a file with first 5 digits of token for "verification code".
    # 2.5. or use some other django package to make that easier
    # 3. have user enter verification code to activate account.
    # Sim validation email with EMAIL_BACKEND and EMAIL_FILE_PATH settings
    # *MUST ADD* actual validation email when deploying to live website. #####


class ProfileDetailView(generic.DetailView):
    permission_classes = (permissions.IsAuthenticated,)
    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        # Add in projects context.
        model = self.request.user
        # print('Avatar Path: {}'.format(model.avatar))
        context['browser'] = self.request.user
        # context['projects'] = Project.objects.filter(creator_id=model.id)
        # Should be able to query this from the user?
        # if so, no reason to query projects at all.
        return context


class ApplicationsView():
    '''
    Allow user to view applicants for each of their projects.
    
    pk: logged-in user.
    context: all projects who have the user as their creator.
    Allow sorting of applicants:
    by status, and/or projects, and/or positions.
    '''
    pass


@login_required
def applications_view(request, pk):
    user = request.user
    project_list = user.projects.all()
    position_list = []
    for project in project_list:
        for position in project.positions.all():
            position_list.append(position)

    applicants = Applicant.objects.filter(position__in=position_list)
    context = {
        'user': user,
        'applicants': applicants,
        'positions': position_list
    }

    return render(request, 'accounts/applications.html', context)