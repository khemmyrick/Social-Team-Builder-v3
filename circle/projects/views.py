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
class ProjectDetailView(DetailView):
    model = promodels.Project
    def get_context_data(self, pk=model.pk):
        # Call the base implementation first to get a context
        context = super(
            ProjectDetailView,
            self
        ).get_context_data(pk=pk)
        # Add in seperate QuerySet ?
        # context['user'] = model.objects.prefetch_related(
        # 'positions',
        # 'projects',
        # 'skills'
        # )
        return context

"""
class ProjectEditView(UpdateView):
    form_class = forms.ProjectForm
    model = promodels.Project
    # fields = ['name', 'url', 'description', 'time', 'requirements']
    template_name_suffix = '_edit'

    def get_success_url(self):
        return redirect('projects:details', pk=model.pk)
"""

def project_detail_view(request, pk):
    """
    Allows a user to view a project.
    """
    user = request.user
    project = promodels.Project.objects.get(id=pk)
    p_list = []
    for position in project.positions.all():
        p_list.append(position)
    if user.is_authenticated:
        applicants = user.applicants.filter(
            position__in=p_list
        )
    else:
        applicants = ''
    # user_skills = user.skills.order_by('name')
    # print("Geting skill data for target user.")
    context = {
        'user': user,
        'project': project,
        'applicants': applicants
    }

    return render(request, 'projects/project_detail.html', context)


def project_update_view(request, pk):
    return HttpResponseRedirect(reverse('projects:details', args=pk))


def project_delete_view(request, pk):
    return HttpResponseRedirect(reverse('projects:details', args=pk))


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
    session_user = request.user
    applicant = promodels.Applicant.objects.get(id=pk)
    position = applicant.position
    # Make sure signed-in user is project creator.
    if position.project.creator != session_user:
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
    return HttpResponseRedirect(
        reverse(
            'accounts:applications',
            pk=session_user.id
        )
    )


@login_required
def application_deny_view(request, pk):
    session_user = request.user
    applicant = promodels.Applicant.objects.get(id=pk)
    position = applicant.position
    # Make sure signed-in user is project creator.
    if position.project.creator != session_user:
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
        pk=session_user.id
    )


class ProjectListView(ListView):
    """
    Render list of projects, set by `self.model` or `self.queryset`.
    `self.queryset` can actually be any iterable of items, not just a queryset.
    """
    # model = models.Project
    queryset = promodels.Project.objects.all()

    # def get_context_data(self, object_list=queryset,**kwargs):
    #    context = super(ArticleListView, self).get_context_data(**kwargs)
    #    # context['now'] = timezone.now()
    #    # What would context['now'] have done?
    #    return context


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
    print('User is {}'.format(project.creator))
    projectdata = {
        'name': project.name,
        'url': project.url,
        'description': project.description,
        'requirements': project.requirements,
        'time': project.time
    }

    # PositionFormSet = formset_factory(
    #    forms.PositionShortForm,
    #    formset=forms.BasePositionFormSet,
    #    extra=0
    # )
    project_positions = project.positions.all().order_by('name')
    # position_data = [{'name': position.name, 
    #                  'description': position.description,
    #                  'pk': position.id}
    #                 for position in project_positions]
    # print(position_data)
    if request.method == 'GET':
        print("Request is get.")
        form = forms.ProjectForm(initial=projectdata)
        print("Project form is created.")
        # formset = PositionFormSet(initial=position_data)
        # print('Position formset created.')
        # GOTO BOTTOM "RETURN" LINE...

    elif request.method == 'POST':
        form = forms.ProjectForm(request.POST, request.FILES, instance=project)
        setattr(form, 'name', project.name)
        print('Project Name: {}'.format(getattr(form, 'name')))
        # formset = PositionFormSet(request.POST, request.FILES)
        # print('Project form and position formset created.')
        # countit = 1
        # for pform in formset:
        #    print('=' * 45)
        #    print(str(countit) + ' ' + str(pform.fields['name']))
        #    countit += 1

        # position_data is our list of dicts for initial positions
        if form.is_valid():
            print('Form is valid.')
            project = form.save()
            messages.success(
                request,
                'You have updated your project.'
            )
            return redirect('projects:details', pk=pk)
            # for position in position_data:
            #    for form in formset:
            #        if form.cleaned_data.get('description'):
            #            if position['id'] == form.cleaned_data.get('pk'):
            #                print('{} == {}'.format(position['id'], form.cleaned_data.get('pk')))
            #                position['description'] = form.cleaned_data.get(
            #                    'description'
            #                )
            #                position['name'] = position['name']
            #                print(
            #                    "{} added to dict.".format(
            #                        position['description']
            #                    )
            #                )
            #            else:
            #                print('{} != {}'.format(position['id'], form.cleaned_data.get('pk')))
            #        else:
            #            if position['id'] == form.cleaned_data.get('id'):
            #                position['description'] = position['description']
            #                position['name'] = position['name']

            # try:
            #    with transaction.atomic():
            #        for position in position_data:
            #            print('Checking {} for update'.format(position['name']))
            #            p_save = promodels.Position.objects.get(id=position['id'])
            #            print('Getting {}'.format(p_save))
            #            print('{} vs {}'.format(p_save.description, position['description']))
            #            if p_save.description != position['description']:
            #                print('Updating {}'.format(position['name']))
            #                p_save.description = position['description']
            #                p_save.save()
            #                messages.success(
            #                    request,
            #                    '{} has been updated!'.format(p_save.name)
            #                )
            #        project.save()
            #        messages.success(request,
            #                         'You have updated your project.')
            #        return redirect('projects:details', pk=pk)
            # except IntegrityError: #If the transaction failed
            #    print("There was an integrity error!")
            #    messages.error(request,
            #                   'There was an error saving your project.')
            #    return redirect('projects:details', pk=pk)

        else:
            print('Form: {}'.format(form))
            print('#' * 80)
            # print('Formset: {}'.format(formset))
            
    return render(
        request,
        'projects/project_edit.html',
        {'form': form,
         # 'formset': formset,
         # 'positions': project_positions,
         'project': project}
    )


class ProjectCreateView(CreateView):
    model = promodels.Project
    # self.object.creator = request.user
    fields = ['name', 'url', 'description', 'time', 'requirements']
    template_name_suffix = '_create'

    def get_success_url(self):
        return redirect('projects:details', pk=self.object.pk)
