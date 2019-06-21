from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic

from . import forms
from projects import forms as pforms
from accounts.models import User
from projects.models import Project, Position, Applicant, Skill
from projects.utils import identify


# Create your views here.
@login_required
def user_update_view(request, pk):
    user = User.objects.get(id=pk)
    if identify(request, user):
        return HttpResponseRedirect(reverse('home'))
    userdata = {
        'display_name': user.display_name,
        'bio': user.bio
    }
    SkillFormSet = formset_factory(pforms.SkillForm,
                                   formset=pforms.BaseSkillFormSet)
    user_skills = user.skills.all().order_by('name')
    skill_data = [{'name': skill.name}
                  for skill in user_skills]
    if request.method == 'GET':
        form = forms.UserForm(initial=userdata)
        formset = SkillFormSet(initial=skill_data)

    elif request.method == 'POST':
        form = forms.UserForm(request.POST, request.FILES, instance=user)
        formset = SkillFormSet(request.POST, request.FILES)
        old_skills = []
        for skill in user.skills.all():
            old_skills.append(skill.name)

        if form.is_valid() and formset.is_valid():
            print('Forms valid.')
            user = form.save()
            new_skills = []

            for skill_form in formset:
                skill_name = skill_form.cleaned_data.get('name')

                if skill_name:
                    new_skills.append(skill_name)

            try:
                with transaction.atomic():
                    for skill in new_skills:
                        add_skill, _ = Skill.objects.get_or_create(name=skill)
                        add_skill.save()
                        add_skill.users.add(user)
                        if skill not in old_skills:
                            messages.success(
                                request,
                                '{} added to skills!'.format(skill)
                            )
                    for skill in old_skills:
                        if skill not in new_skills:
                            old_skill = Skill.objects.get(name=skill)
                            old_skill.save()
                            old_skill.users.remove(user)
                            messages.success(
                                request,
                                '{} removed from skills!'.format(skill)
                            )
                    user.save()

                    messages.success(request,
                                     'You have updated your profile.')

            except IntegrityError:
                messages.error(request,
                               'There was an error saving your profile.')
                return redirect('accounts:details', pk=pk)

    return render(
        request,
        'accounts/user_form.html',
        {'form': form, 'formset': formset}
    )


def user_detail_view(request, pk):
    """
    Allows a user to update their own user.
    """
    user = request.user
    target_user = User.objects.get(id=pk)
    user_skills = user.skills.order_by('name')
    skill_data = [{'name': skill}
                  for skill in user_skills]

    context = {
        'user': user,
        'target_user': target_user,
        'skills': skill_data
    }

    return render(request, 'accounts/user_detail.html', context)


@login_required
def user_deactivate_view(request, pk):
    """Allows a user to deactivate their account."""
    target_user = User.objects.get(id=pk)
    if identify(request, target_user):
        return HttpResponseRedirect(reverse('home'))
    return render(
        request,
        'projects/delete.html',
        {'target_user': target_user}
    )


@login_required
def user_deactivate_confirm_view(request, pk):
    """Confirm user account deactivation."""
    target_user = User.objects.get(id=pk)
    if identify(request, target_user):
        return HttpResponseRedirect(reverse('home'))
    target_user.is_active = False
    target_user.save()
    messages.success(request, 'Your account has been deactivated.')
    return HttpResponseRedirect(reverse('accounts:logout'))


class LogInView(generic.FormView):
    form_class = AuthenticationForm
    success_url = reverse_lazy("home")
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


@login_required
def applications_view_byproject(request, pk, term):
    user = User.objects.get(id=pk)
    if identify(request, user):
        return HttpResponseRedirect(reverse('home'))
    project = Project.objects.get(name=term)
    # position = Position.objects.get(name=term)
    position_list = []
    position_qs = project.positions.all()
    for position in position_qs:
        position_list.append(position)
    # project_list = user.projects.all()
    # for project in project_list:
    #    for position in project.positions.all():
    #        position_list.append(position)
    applicants = Applicant.objects.filter(position__in=position_list)
    context = {
        'user': user,
        'applicants': applicants,
        'positions': position_list,
        'term': term
    }
    return render(request, 'accounts/applications.html', context)


@login_required
def applications_view_byposition(request, pk, term):
    user = User.objects.get(id=pk)
    if identify(request, user):
        return HttpResponseRedirect(reverse('home'))
    position = Position.objects.get(name=term)
    position_list = []
    position_list.append(position)
    # project_list = user.projects.all()
    # for project in project_list:
    #    for position in project.positions.all():
    #        position_list.append(position)
    applicants = Applicant.objects.filter(position=position)
    context = {
        'user': user,
        'applicants': applicants,
        'positions': position_list,
        'term': term
    }
    return render(request, 'accounts/applications.html', context)


@login_required
def applications_view_bystatus(request, pk, term):
    user = User.objects.get(id=pk)
    if identify(request, user):
        return HttpResponseRedirect(reverse('home'))
    position_list = []
    project_list = user.projects.all()
    for project in project_list:
        for position in project.positions.all():
            position_list.append(position)
    applicants = Applicant.objects.filter(
        position__in=position_list
    ).filter(status=term)
    context = {
        'user': user,
        'applicants': applicants,
        'positions': position_list,
        'term': term
    }
    return render(request, 'accounts/applications.html', context)


@login_required
def applications_view(request, pk):
    """Display all users applying for current user's open projects."""
    user = User.objects.get(id=pk)
    if identify(request, user):
        return HttpResponseRedirect(reverse('home'))
    project_list = user.projects.all()
    position_list = []
    for project in project_list:
        for position in project.positions.all():
            position_list.append(position)

    applicants = Applicant.objects.filter(position__in=position_list)

    context = {
        'user': user,
        'applicants': applicants,
        'positions': position_list,
        'term': ''
    }

    return render(request, 'accounts/applications.html', context)
