from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.forms import inlineformset_factory, formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from accounts import forms
from . import models as promodels


# Create your views here.
@login_required
def position_create_view(request, pk):
    project = promodels.Project.objects.get(id=pk)
    if request.user != project.creator:
        messages.error(
            request,
            "You must be logged in as {} to do this.".format(project.creator)
        )
        return HttpResponseRedirect(reverse('home'))

    positiondata = {'project': project}
    SkillFormSet = formset_factory(forms.SkillForm,
                                   formset=forms.BaseSkillFormSet)
    # No skill data yet!
    # position_skills = position.skills.all().order_by('name')
    # skill_data = [{'name': skill.name}
    #               for skill in position_skills]
    if request.method == 'GET':
        print("Request is get.")
        form = forms.PositionForm(initial=positiondata)
        print("User form is created.")
        formset = SkillFormSet()
        # GOTO BOTTOM "RETURN" LINE...

    elif request.method == 'POST':
        form = forms.PositionForm(request.POST, request.FILES) #instance=project?
        formset = SkillFormSet(request.POST, request.FILES)
        # old_skills = []
        # for skill in position.skills.all():
        #    old_skills.append(skill.name)

        if form.is_valid() and formset.is_valid():
            print('Forms valid.')
            positiondata['name'] = form.cleaned_data.get('name')
            positiondata['description'] = form.cleaned_data.get('description')
            position = promodels.Position(
                name=positiondata['name'],
                description=positiondata['description'],
                project=positiondata['project']
            )
            position.save()
            new_skills = []

            for skill_form in formset:
                skill_name = skill_form.cleaned_data.get('name')

                if skill_name:
                    new_skills.append(skill_name)

            try:
                with transaction.atomic():
                    for skill in new_skills:
                        add_skill, _ = promodels.Skill.objects.get_or_create(
                            name=skill
                        )
                        add_skill.save()
                        add_skill.positions.add(position)
                        messages.info(
                            request,
                            '{} added to skills!'.format(skill)
                        )
                    position.save()

                    messages.success(request,
                                     'You have updated your position.')

            except IntegrityError: #If the transaction failed
                messages.error(request,
                               'There was an error creating this position.')
                return redirect('projects:details', pk=pk)

    return render(
        request,
        'projects/position_form.html',
        {'form': form, 'formset': formset, 'project': project}
    )


@login_required
def position_update_view(request, pk, pospk):
    project = promodels.Project.objects.get(id=pk)
    if request.user != project.creator:
        messages.error(
            request,
            "You must be logged in as {} to do this.".format(project.creator)
        )
        return HttpResponseRedirect(reverse('home'))
    position = promodels.Position.objects.get(id=pospk)
    positiondata = {
        'name': position.name,
        'description': position.description,
        'project': project,
        'time': position.time,
        'id': position.id
    }
    SkillFormSet = formset_factory(forms.SkillForm,
                                   formset=forms.BaseSkillFormSet)
    position_skills = position.skills.all().order_by('name')
    skill_data = [{'name': skill.name}
                   for skill in position_skills]
    if request.method == 'GET':
        print("Request is get.")
        form = forms.PositionForm(initial=positiondata)
        print("User form is created.")
        formset = SkillFormSet(initial=skill_data)
        # GOTO BOTTOM "RETURN" LINE...

    elif request.method == 'POST':
        form = forms.PositionForm(request.POST, request.FILES, instance=position) #instance=project?
        formset = SkillFormSet(request.POST, request.FILES)
        old_skills = []
        for skill in position.skills.all():
            old_skills.append(skill.name)

        if form.is_valid() and formset.is_valid():
            print('Forms valid.')
            # position = form.save()
            position = promodels.Position.objects.get(id=pospk)
            position.name = form.cleaned_data.get('name')
            position.description = form.cleaned_data.get('description')
            position.id = positiondata['id']
            position.save()
            new_skills = []

            for skill_form in formset:
                skill_name = skill_form.cleaned_data.get('name')

                if skill_name:
                    new_skills.append(skill_name)

            try:
                with transaction.atomic():
                    for skill in new_skills:
                        add_skill, _ = promodels.Skill.objects.get_or_create(
                            name=skill
                        )
                        add_skill.save()
                        add_skill.positions.add(position)
                        if add_skill not in old_skills:
                            messages.info(
                                request,
                                '{} added to skills!'.format(skill)
                            )
                    for skill in old_skills:
                        if skill not in new_skills:
                            old_skill = Skill.objects.get(name=skill)
                            old_skill.save()
                            old_skill.users.remove(user)
                            messages.info(
                                request,
                                '{} removed from skills!'.format(skill)
                            )
                    position.save()

                    messages.success(request,
                                     'You have updated your position.')

            except IntegrityError: #If the transaction failed
                messages.error(request,
                               'There was an error creating this position.')
                return redirect('projects:details', pk=pk)

    return render(
        request,
        'projects/position_form.html',
        {'form': form, 'formset': formset, 'project': project, 'position': position}
    )


def project_detail_view(request, pk):
    """
    Allows a user to view a project.
    """
    project = promodels.Project.objects.get(id=pk)
    if not project.active:
        if request.user == project.creator:
            return render(
                request, 
                'projects/activate.html',
                {'project': project}
            )
        messages.info(
            request,
            'That project is inactive.'
        )
        return redirect('home')
    context = {
        'project': project,
    }
    return render(
        request,
        'projects/project_detail.html',
        {'project': project}
    )


def project_suspend_view(request, pk):
    project = promodels.Project.objects.get(id=pk)
    return render(
        request,
        'projects/delete.html',
        {'project': project}
    )


def project_suspend_confirm_view(request, pk):
    project = promodels.Project.objects.get(id=pk)
    project.active = False
    project.save()
    messages.success(
        request,
        'Your project has been suspended.'.format(project.name)
    )
    return redirect('home')


# def project_activate_view(request, pk):
#    project = promodels.Project.objects.get(id=pk)
#    project.active = True
#    return render(
#        request,
#        'projects/activate.html',
#        {'project': project}
#    )


def project_confirm_activate_view(request, pk):
    project = promodels.Project.objects.get(id=pk)
    project.active = True
    project.save()
    messages.success(
        request,
        'Your project, {}, has resumed.'.format(project.name)
    )
    return render(
        request,
        'projects/project_detail.html',
        {'project': project}
    )


def position_delete_view(request, pk, pospk):
    position = promodels.Position.objects.get(id=pospk)
    return render(
        request,
        'projects/delete.html',
        {'position': position}
    )


def position_delete_confirm_view(request, pk, pospk):
    position = promodels.Position.objects.get(id=pospk)
    position.delete()
    messages.success(
        request,
        'Position deleted successfully.'
    )
    return redirect('home')


def position_name_view(request, term):
    """
    Allows users to view list of each project needing a certain position.
    """
    term = term
    user = request.user
    positions = promodels.Position.objects.filter(
        name=term
    )
    p_names = [position.name for position in positions]
    p_names = set(p_names)
    p_names = list(p_names)
    positions = positions.filter(filled=False)
    context = {
        'user': user,
        'positions': positions,
        'term': term,
        'p_names': p_names
    }
    
    return render(request, 'projects/project_list.html', context)


def position_list_view(request):
    """
    Allows users to view list of project positions.
    """
    term = request.GET.get('q')
    user = request.user
    # positions = promodels.Position.objects.filter(filled=False)
    if term:
        positions = promodels.Position.objects.filter(
            filled=False
        ).filter(
            Q(name__icontains=term)|
            Q(description__icontains=term)|
            Q(time__icontains=term)|
            Q(project__name__icontains=term)|
            Q(project__description__icontains=term)|
            Q(project__creator__display_name__icontains=term)
        ) # .values(
        #    'name',
        #    'project.name',
        #    'project.id',
        #    'project.creator.display_name'
        # )
    else:
        positions = promodels.Position.objects.filter(filled=False)
        term = ''
    all_pos = promodels.Position.objects.all()
    p_names = [position.name for position in all_pos]
    p_names = set(p_names)
    p_names = list(p_names)
    context = {
        'user': user,
        'positions': positions,
        'term': term,
        'p_names': p_names
    }
    
    return render(request, 'projects/project_list.html', context)


@login_required
def application_create_view(request, pk):
    user = request.user
    position = promodels.Position.objects.get(id=pk)
    try:
        applicant = promodels.Applicant(
            user=user,
            position=position
        )
        applicant.save()
    except ValidationError:
        messages.error(request, "You've already applied for this position.")
        return HttpResponseRedirect(reverse('home'))

    messages.success(
        request,
        'You applied for the {} role!'.format(position.name)
    )
    return HttpResponseRedirect(reverse('home'))


@login_required
def application_accept_view(request, pk):
    applicant = promodels.Applicant.objects.get(id=pk)
    position = applicant.position
    # Make sure signed-in user is project creator.
    if position.project.creator != request.user:
        messages.error(
            request,
            "You must be the project creator to do that!"
        )
        return HttpResponseRedirect(reverse('home'))
    # If session_user is project.creator, accept applicant for position.
    applicant.status = 'a'
    applicant.save()
    position.user = applicant.user
    position.filled = True
    position.save()
    messages.success(
        request,
        "You accepted {} as {}.".format(position.user, position.name)
    )
    return redirect(
        'accounts:applications',
        pk=request.user.id
    )


@login_required
def application_deny_view(request, pk):
    applicant = promodels.Applicant.objects.get(id=pk)
    position = applicant.position
    # Make sure signed-in user is project creator.
    if position.project.creator != request.user:
        messages.error(
            request,
            "You must be the project creator to do that!"
        )
        return HttpResponseRedirect(reverse('home'))
    # If session_user is project.creator, rejectt applicant for position.
    applicant.status = 'r'
    applicant.save()
    position.user = applicant.user
    position.filled = True
    position.save()
    messages.success(
        request,
        "{} won't be joining the team as {}.".format(
            position.user,
            position.name
        )
    )
    return redirect(
        'accounts:applications',
        pk=request.user.id
    )


@login_required
def project_create_view(request):
    user = request.user
    project_data = {'creator': user}
    if request.method == 'GET':
        form = forms.ProjectCreateForm(initial=project_data)
    elif request.method == 'POST':
        form = forms.ProjectCreateForm(request.POST, request.FILES)
        if form.is_valid():
            print('Form is valid.')
            # manually save object
            project_data['name'] = form.cleaned_data.get('name')
            project_data['url'] = form.cleaned_data.get('url')
            project_data['description'] = form.cleaned_data.get('description')
            project_data['time'] = form.cleaned_data.get('time')
            project_data['requirements'] = form.cleaned_data.get('requirements')
            project = promodels.Project(
                name=project_data['name'],
                url=project_data['url'],
                description=project_data['description'],
                creator=project_data['creator'],
                requirements=project_data['requirements'],
                time=project_data['time']                
            )
            project.save()
            messages.success(
                request,
                'You have created a new project!'
            )
            return redirect('projects:details', pk=project.id)
    context = {'form': form}
    return render(
        request,
        'projects/project_create.html',
        {'form': form}
    )

@login_required
def project_update_view(request, pk):
    project = promodels.Project.objects.get(id=pk)
    if request.user != project.creator:
        messages.error(
            request,
            "You must be logged in as {} to do this.".format(project.creator)
        )
        return HttpResponseRedirect(reverse('home'))
    projectdata = {
        'name': project.name,
        'url': project.url,
        'description': project.description,
        'requirements': project.requirements,
        'time': project.time
    }
    if request.method == 'GET':
        print("Request is get.")
        form = forms.ProjectForm(initial=projectdata)
        print("Project form is created.")

    elif request.method == 'POST':
        form = forms.ProjectForm(request.POST, request.FILES, instance=project)
        setattr(form, 'name', project.name)
        if form.is_valid():
            print('Form is valid.')
            project = form.save()
            messages.success(
                request,
                'You have updated your project.'
            )
            return redirect('projects:details', pk=pk)

        else:
            messages.failure(
                request,
                'Something went wrong. We were unable to update your project.'
            )
            return redirect('projects:details', pk=pk)
            
    return render(
        request,
        'projects/project_edit.html',
        {'form': form,
         'project': project}
    )


class ProjectCreateView(CreateView):
    model = promodels.Project
    # self.object.creator = request.user
    fields = ['name', 'url', 'description', 'time', 'requirements']
    template_name_suffix = '_create'

    def get_success_url(self):
        return redirect('projects:details', pk=self.object.pk)
