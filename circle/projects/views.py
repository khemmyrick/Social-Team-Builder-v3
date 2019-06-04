from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

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
    # Make sure signed-in user is project creator.
    if applicant.project.creator != session_user:
        messages.error(
            request,
            "You must be the project creator to do that!"
        )
        return HttpResponseRedirect(reverse('home'))
    # If session_user is project.creator, accept applicant for position.
    applicant.status = 'a'
    applicant.save()
    position = applicant.position
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
