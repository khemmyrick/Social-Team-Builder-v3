from django.shortcuts import render
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
    applicant = user.applicants.filter(position__in=p_list).first()
    # user_skills = user.skills.order_by('name')
    # print("Geting skill data for target user.")
    context = {
        'user': user,
        'project': project,
        'applicant': applicant
    }

    return render(request, 'projects/project_detail.html', context)


def position_list_view(request):
    """
    Allows users to view project list.
    """
    user = request.user
    positions = promodels.Position.objects.filter(filled=False)
    context = {
        'user': user,
        'positions': positions,
    }
    
    return render(request, 'projects/project_list.html', context)

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
