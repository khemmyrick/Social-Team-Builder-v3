from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from projects import forms as forms
from projects.models import Project, Position, Applicant, Skill
from projects.utils import identify


# Create your views here.
@login_required
def position_create_view(request, pk):
    project = Project.objects.get(id=pk)
    if identify(request, project.creator):
        return HttpResponseRedirect(reverse('home'))

    positiondata = {'project': project}
    SkillFormSet = formset_factory(forms.SkillForm,
                                   formset=forms.BaseSkillFormSet)
    if request.method == 'GET':
        form = forms.PositionForm(initial=positiondata)
        formset = SkillFormSet()
        # GOTO BOTTOM "RETURN" LINE...

    elif request.method == 'POST':
        form = forms.PositionForm(request.POST, request.FILES)
        formset = SkillFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            print('Forms valid.')
            positiondata['name'] = form.cleaned_data.get('name')
            positiondata['description'] = form.cleaned_data.get('description')
            positiondata['time'] = form.cleaned_data.get('time')
            position = Position(
                name=positiondata['name'],
                description=positiondata['description'],
                time=positiondata['time'],
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
                        add_skill, _ = Skill.objects.get_or_create(
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

            except IntegrityError:
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
    project = Project.objects.get(id=pk)
    if identify(request, project.creator):
        return HttpResponseRedirect(reverse('home'))
    position = Position.objects.get(id=pospk)
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
        form = forms.PositionForm(initial=positiondata)
        formset = SkillFormSet(initial=skill_data)
        # GOTO BOTTOM "RETURN" LINE...

    elif request.method == 'POST':
        form = forms.PositionForm(
            request.POST,
            request.FILES,
            instance=position
        )
        formset = SkillFormSet(request.POST, request.FILES)
        old_skills = []
        for skill in position.skills.all():
            old_skills.append(skill.name)

        if form.is_valid() and formset.is_valid():
            print('Forms valid.')
            position = Position.objects.get(id=pospk)
            position.name = form.cleaned_data.get('name')
            position.description = form.cleaned_data.get('description')
            position.time = form.cleaned_data.get('time')
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
                        add_skill, _ = Skill.objects.get_or_create(
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
                            old_skill.positions.remove(position)
                            messages.info(
                                request,
                                '{} removed from skills!'.format(skill)
                            )
                    position.save()

                    messages.success(request,
                                     'You have updated your position.')

            except IntegrityError:
                messages.error(request,
                               'There was an error creating this position.')
                return redirect('projects:details', pk=pk)

    context = {
        'form': form,
        'formset': formset,
        'project': project,
        'position': position
    }
    return render(request, 'projects/position_form.html', context)


def project_detail_view(request, pk):
    """
    Allows a user to view a project.
    """
    project = Project.objects.get(id=pk)
    if not project.active:
        if identify(request, project.creator):
            return HttpResponseRedirect(reverse('home'))
        else:
            return render(
                request,
                'projects/activate.html',
                {'project': project}
            )
    positions = project.positions.all()
    position_list = []
    for position in positions:
        position_list.append(position)
    if request.user.is_authenticated:
        applicants = request.user.applicants.filter(position__in=position_list)
    else:
        applicants = ''
    return render(
        request,
        'projects/project_detail.html',
        {'project': project, 'applicants': applicants}
    )


def position_detail_view(request, pk, pospk):
    """Allows a user to view a position."""
    position = Position.objects.get(id=pospk)
    if not position.active:
        if identify(request, position.project.creator):
            return HttpResponseRedirect(reverse('home'))
        else:
            return render(
                request,
                'projects/activate.html',
                {'project': position.project}
            )
    applicants = request.user.applicants.filter(position=position)
    return render(
        request,
        'projects/position_detail.html',
        {'position': position, 'applicants': applicants}
    )


def project_suspend_view(request, pk):
    project = Project.objects.get(id=pk)
    if identify(request, project.creator):
        return HttpResponseRedirect(reverse('home'))
    return render(
        request,
        'projects/delete.html',
        {'project': project}
    )


def project_suspend_confirm_view(request, pk):
    project = Project.objects.get(id=pk)
    if identify(request, project.creator):
        return HttpResponseRedirect(reverse('home'))
    for position in project.positions.all():
        position.active = False
        position.save()
    project.active = False
    project.save()
    messages.success(
        request,
        'Your project has been suspended.'.format(project.name)
    )
    return redirect('home')


def project_confirm_activate_view(request, pk):
    project = Project.objects.get(id=pk)
    if identify(request, project.creator):
        return HttpResponseRedirect(reverse('home'))
    project.active = True
    project.save()
    for position in project.positions.all():
        position.active = True
        position.save()
    messages.success(
        request,
        'Your project, {}, has resumed.'.format(project.name)
    )
    return render(
        request,
        'projects/project_detail.html',
        {'project': project}
    )


def position_name_view(request, term):
    """
    Allows users to view list of each project needing a certain position.
    """
    term = term
    user = request.user
    positions = Position.objects.filter(
        name=term
    )
    p_names = [position.name for position in positions]
    p_names = set(p_names)
    p_names = list(p_names)
    positions = positions.filter(filled=False)

    ds_list = []
    if request.user.is_authenticated:
        for position in positions:
            compatibility = 0
            for skill in position.skills.all():
                if skill in user.skills.all():
                    compatibility += 1
            if compatibility == len(position.skills.all()):
                ds_list.append(position.id)

    showall = '1'
    context = {
        'user': user,
        'positions': positions,
        'term': term,
        'p_names': p_names,
        'dslist': ds_list,
        'showall': showall
    }

    return render(request, 'projects/project_list.html', context)


def position_list_view(request, showall=None):
    """
    Allows users to view list of project positions.
    """
    term = request.GET.get('q')
    user = request.user
    if term:
        positions = Position.objects.filter(
            filled=False
        ).filter(
            Q(name__icontains=term) |
            Q(description__icontains=term) |
            Q(time__icontains=term) |
            Q(project__name__icontains=term) |
            Q(project__description__icontains=term) |
            Q(project__creator__display_name__icontains=term)
        )
    else:
        positions = Position.objects.filter(filled=False)
        term = ''

    ds_list = []
    if request.user.is_authenticated:
        for position in positions:
            compatibility = 0
            for skill in position.skills.all():
                if skill in user.skills.all():
                    compatibility += 1
            if compatibility == len(position.skills.all()):
                ds_list.append(position.id)

    p_names = [position.name for position in positions]
    p_names = set(p_names)
    p_names = list(p_names)
    if user.is_authenticated == False:
        showall = '1'
    if showall:
        pass
    else:
        showall = ''
    context = {
        'user': user,
        'positions': positions,
        'term': term,
        'p_names': p_names,
        'dslist': ds_list,
        'showall': showall
    }

    return render(request, 'projects/project_list.html', context)


@login_required
def application_create_view(request, pk):
    user = request.user
    position = Position.objects.get(id=pk)
    try:
        applicant = Applicant(
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
    applicant = Applicant.objects.get(id=pk)
    position = applicant.position
    if identify(request, position.project.creator):
        return HttpResponseRedirect(reverse('home'))
    applicant.status = 'a'
    applicant.save()
    position.user = applicant.user
    position.filled = True
    position.save()

    # Automatically reject all other applicants.
    reject_list = []
    runner_ups = position.applicants.exclude(user=position.user)
    for applicant in runner_ups:
        reject_list.append(applicant)
    for applicant in reject_list:
        applicant.status = 'r'
        applicant.save()
        # Email rejections here.
        applicant.user.email_user(
            subject="We're going in another direction for our {}.".format(
                position.name
            ),
            message="Look out for other opportunities from us in the future.",
            from_email=request.user.email
        )

    position.user.email_user(
        subject="Hello, new {}!".format(position.name),
        message="We look forward to working with you on this project.",
        from_email=request.user.email
    )
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
    applicant = Applicant.objects.get(id=pk)
    position = applicant.position
    if identify(request, position.project.creator):
        return HttpResponseRedirect(reverse('home'))
    applicant.status = 'r'
    applicant.save()
    position.user = applicant.user
    position.filled = True
    position.save()
    position.user.email_user(
        subject="We're going in another direction for our {}.".format(
            position.name
        ),
        message="Look out for other opportunities from us in the future.",
        from_email=request.user.email
    )
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
            project_data['name'] = form.cleaned_data.get('name')
            project_data['url'] = form.cleaned_data.get('url')
            project_data['description'] = form.cleaned_data.get('description')
            project_data['time'] = form.cleaned_data.get('time')
            project_data['requirements'] = form.cleaned_data.get(
                'requirements'
            )
            project = Project(
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

    return render(
        request,
        'projects/project_create.html',
        {'form': form}
    )


@login_required
def project_update_view(request, pk):
    project = Project.objects.get(id=pk)
    if identify(request, project.creator):
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
