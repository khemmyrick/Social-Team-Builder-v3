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
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django_registration.views import ActivationView

from extra_views import (InlineFormSetFactory, CreateWithInlinesView,
                         UpdateWithInlinesView)

from rest_framework import generics, permissions, status
from rest_framework.response import Response

import pdb

from . import forms
from accounts.models import User, Skill
from projects.models import Project, Applicant


# Create your views here.
@login_required
def user_update_view(request, pk):
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
        form = forms.UserUpdateForm(initial=userdata)
        print("User form is created.")
        # GOTO BOTTOM "RETURN" LINE...
    elif request.method == 'POST':
        form = forms.UserUpdateForm(request.POST, request.FILES, instance=user) #instance=user?
        if form.is_valid():
            user = form.save() # args? update_fields=['display_name', 'bio']
            return redirect('accounts:details', pk=pk)

    return render(request, 'accounts/user_form.html', {'form': form})


@login_required
def skills_update_view(request, pk):
    """
    Allows a user to update their own profile.
    """
    user = User.objects.get(id=pk)
    if request.user.id != user.id:
        messages.error(
            request,
            "You must be logged in as {} to do this.".format(user.username)
        )
        return HttpResponseRedirect(reverse('home'))
    # Create the formset, specifying the form and formset we want to use.
    SkillFormSet = formset_factory(forms.SkillForm, formset=forms.BaseSkillFormSet)

    # Get our existing skill data for this user.  This is used as initial data.
    # MAKE SKILL A LIST!
    user_skills = user.get_skill_list()
    # user_skills = user.skills.all().order_by('name')
    skill_data = [{'name': skill}
                   for skill in user_skills]

    if request.method == 'POST':
        skill_formset = SkillFormSet(request.POST)

        if skill_formset.is_valid():
            # Save user info
            # user = form.save()
            
            # Now save the data for each form in the formset
            new_skills = []

            for skill_form in skill_formset:
                skill_name = skill_form.cleaned_data.get('name')

                if skill_name:
                    new_skills.append(skill_name)

            try:
                with transaction.atomic():
                    #Replace the old with the new
                    
                    # UserLink.objects.filter(user=user).delete()
                    # UserLink.objects.bulk_create(new_links)
                    # Turn new skill list into comma seperated str
                    user.skill_list = ', '.join(new_skills)
                    user.save()
                    # And notify our users that it worked
                    messages.success(request, 'You have updated your profile.')

            except IntegrityError: #If the transaction failed
                messages.error(request, 'There was an error saving your profile.')
                return redirect(reverse('profile-settings'))

    else:
        skill_formset = SkillFormSet(initial=skill_data)

    context = {
        'formset': skill_formset,
    }

    return render(request, 'accounts/skill_form.html', context)

"""
@login_required
def skills_update_view(request, pk):
    user = User.objects.get(id=pk)
    if request.user.id != user.id:
        messages.error(
            request,
            "You must be logged in as {} to do this.".format(user.username)
        )
        return HttpResponseRedirect(reverse('home'))
    template_name = 'accounts/skill_form.html'
    heading_message = 'Skill Formset'
    if request.method == 'GET':
        formset = forms.SkillFormset(request.GET or None)
    elif request.method == 'POST':
        formset = forms.SkillFormset(request.POST)
        if formset.is_valid():
            for form in formset:
                # extract name from each form and save
                name = form.cleaned_data.get('name')
                # save skill instance
                if name:
                    # Skill(name=name).save()
                    skill, _ = Skill.objects.update_or_create(
                        name=name,
                        defaults={'name': name}
                    )
                    print('Adding {}'.format(skill))
                    skill.users.add(user)
            # once all skills are saved, redirect to skill list view
            user.save()
            return redirect('accounts:details', pk=user.id)
    return render(request, template_name, {
        'formset': formset,
        'heading': heading_message,
    })
"""

"""
@login_required
def skills_update_view(request, pk):
    user = User.objects.get(id=pk)
    if request.user.id != user.id:
        messages.error(
            request,
            "You must be logged in as {} to do this.".format(user.username)
        )
        return HttpResponseRedirect(reverse('home'))
    template_name = 'accounts/skill_form.html'
    heading_message = 'Skill Formset'
    if request.method == 'GET':
        formset = forms.SkillFormset(request.GET or None)
    elif request.method == 'POST':
        formset = forms.SkillFormset(request.POST)
        if formset.is_valid():
            for form in formset:
                # extract name from each form and save
                name = form.cleaned_data.get('name')
                # save skill instance
                if name:
                    # Skill(name=name).save()
                    skill, _ = Skill.objects.update_or_create(
                        name=name,
                        defaults={'name': name}
                    )
                    print('Adding {}'.format(skill))
                    skill.users.add(user)
            # once all skills are saved, redirect to skill list view
            user.save()
            return redirect('accounts:details', pk=user.id)
    return render(request, template_name, {
        'formset': formset,
        'heading': heading_message,
    })
"""

def user_detail_view(request, pk):
    """
    Allows a user to update their own user.
    """
    user = request.user
    print("1. Session user object.")
    target_user = User.objects.get(id=pk)
    print("2. Getting user user.")
    user_skills = target_user.get_skill_list()
    skill_data = [{'name': skill}
                   for skill in user_skills]
    # user_skills = user.skills.order_by('name')
    # print("Geting skill data for target user.")
    context = {
        'user': user,
        'target_user': target_user,
        'skills': skill_data
    }
    print("3. Context is created.")
    # Is this the initial load of the edit template?

    return render(request, 'accounts/user_detail.html', context)


class UserUpdateView(generic.UpdateView):
    model = get_user_model()
    fields = ['username', 'display_name', 'bio', 'avatar']
    success_url = reverse_lazy('home')


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


class UserDetailView(generic.DetailView):
    permission_classes = (permissions.IsAuthenticated,)
    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
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