import os.path

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

from PIL import Image

from . import forms
from projects import forms as pforms
from accounts.models import User, user_directory_path
from projects.models import Project, Applicant, Skill
from projects.utils import identify, show_messages


# Create your views here.
@login_required
def user_update_view(request, pk):
    """
    If session user is target user, update account details.
    Else, redirect to home page.

    pk: Target user's id.
    """
    show_messages(request)
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
    View target user's account details.

    pk: Target user's id.
    """
    show_messages(request)
    user = request.user
    target_user = User.objects.get(id=pk)
    if not request.user.is_authenticated:
        if not target_user.is_active:
            return redirect('accounts:reactivate', pk=pk)

    user_skills = user.skills.order_by('name')
    skill_data = [{'name': skill}
                  for skill in user_skills]

    context = {
        'user': user,
        'target_user': target_user,
        'skills': skill_data
    }

    return render(request, 'accounts/user_detail.html', context)


def avatar_view(request, pk):
    """
    View target user's avatar.
    
    pk: Target user's id.
    """
    show_messages(request)
    target_user = User.objects.get(id=pk)
    context = {'user': request.user, 'target_user': target_user}
    return render(request, 'accounts/user_photo.html', context)


@login_required
def user_deactivate_view(request, pk):
    """
    If session user is target user,
    get confirmation for account deactivation.
    Else, redirect to homepage and do nothing.

    pk: User's id.
    """
    show_messages(request)
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
    """
    If session user is target user, deactivate account.
    Else, redirect to home page and do nothing.

    pk: User's id.
    """
    target_user = User.objects.get(id=pk)
    if identify(request, target_user):
        return HttpResponseRedirect(reverse('home'))
    target_user.is_active = False
    target_user.save()
    messages.success(request, 'Your account has been deactivated.')
    return HttpResponseRedirect(reverse('accounts:logout'))


class LogInView(generic.FormView):
    """Log in a session user."""
    form_class = AuthenticationForm
    success_url = reverse_lazy("home")
    template_name = "accounts/signin.html"

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request, **self.get_form_kwargs())

    def form_valid(self, form):
        login(self.request, form.get_user())
        show_messages(self.request)
        # messages.info(self.request, form.get_user().notifications)
        return super().form_valid(form)


class LogOutView(generic.RedirectView):
    """Logout a session user."""
    url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        # request.user.notifications = ''
        # request.user.save()
        logout(request)
        return super().get(request, *args, **kwargs)


@login_required
def applications_view_byproject(request, pk, term):
    """
    Filter applicants by project.

    pk: Session user's id.
    term: Name of the project.
    """
    show_messages(request)
    user = User.objects.get(id=pk)
    if identify(request, user):
        return HttpResponseRedirect(reverse('home'))
    project = Project.objects.get(name=term)
    position_list = []
    position_qs = project.positions.all()
    for position in position_qs:
        position_list.append(position)
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
    """
    Filter applicants by position they've applied for.

    pk: Session user's id.
    term: Name of position or positions.
    """
    show_messages(request)
    user = User.objects.get(id=pk)
    if identify(request, user):
        return HttpResponseRedirect(reverse('home'))
    position_list = []
    project_list = user.projects.all()
    for project in project_list:
        for position in project.positions.all():
            if position.name == term:
                position_list.append(position)
    applicants = Applicant.objects.filter(position__in=position_list)
    context = {
        'user': user,
        'applicants': applicants,
        'positions': position_list,
        'term': term
    }
    return render(request, 'accounts/applications.html', context)


@login_required
def applications_view_bystatus(request, pk, term):
    """
    Filter applicants by application status.

    pk: Session user's id.
    term:
        'a': accepted
        'r': rejected
        'u': undecided
    """
    show_messages(request)
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
    """
    Display all applicants for session user's open projects.

    pk: Session user's id.
    """
    show_messages(request)
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


def user_reactivate_view(request, pk):
    """
    Enable a disabled user's account.

    pk: The user id.
    """
    # Work in progress.
    if request.user.is_authenticated:
        return redirect('home')
    user = User.objects.get(id=pk)
    userdata = {
        'email': user.email,
        'username': user.username,
        'password': user.password,
        'password2': user.password
    }
    if request.method == 'POST':
        form = forms.UserRegistrationForm(request.POST)
        if form.is_valid():
            if userdata['username'] == form.cleaned_data.get('username') and \
               userdata['email'] == form.cleaned_data.get('email') and \
               userdata['password'] == user.set_password(
                   form.cleaned_data.get('password')
            ):
                user.is_active = True
                user.save()
                messages.success(request, 'Your account is reactivated.')
                return redirect('accounts:details', pk=pk)
        messages.info(request, 'Credentials incorrect.')
        return redirect('home')
    form = forms.UserRegistrationForm()
    context = {'form': form, 'pk': pk}
    return render(request, 'accounts/reactivate.html', context)


@login_required
def avatar_update_view(request, pk):
    """
    Upload or replace a user's avatar.
    If session user is not target user, redirect to home page.

    pk: Target user's id.
    """
    show_messages(request)
    user = User.objects.get(id=pk)
    if identify(request, user):
        return HttpResponseRedirect(reverse('home'))
    if request.method == 'POST':
        form = forms.PhotoForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your user photo has been updated.')
            return redirect('accounts:details', pk=pk)
    else:
        form = forms.PhotoForm()
    context = {'form': form, 'user': user}
    return render(request, 'accounts/photo_form.html', context)


@login_required
def avatar_edit_view(request, pk):
    """Edit avatar."""
    target_user = User.objects.get(id=pk)
    avaname = target_user.username
    if identify(request, target_user):
        return HttpResponseRedirect(reverse('home'))
    if not target_user.avatar:
        return redirect('accounts:updatephoto', pk=pk)
    avatype = target_user.avatar.path[-4:]
    # check for image type
    if os.path.exists('media/avatars/{}{}'.format(avaname, avatype)):
        print('Found temp avatar!')
        print('User.avatar.url is: {}'.format(target_user.avatar.url))
        avatar = Image.open('media/avatars/{}{}'.format(avaname, avatype))
        temp_path = 'media/avatars/{}{}'.format(avaname, avatype)
        # avatar = Image.open(temp_avatar)
        # temp avatar is a str of the user's username. use to make str to path.
    else:
        print('No temp avatar found.')
        temp_path = ''
        avatar = Image.open(target_user.avatar.path)

    ava_w, ava_h = avatar.size
    form = forms.PhotoEditForm()

    if request.method == 'POST':
        print('Request is POST.')
        temp_path = 'media/avatars/{}{}'.format(
            avaname,
            avatype
        )
        print('temp_path set. to {}'.format(temp_path))
        form = forms.PhotoEditForm(request.POST)
        print('Checking form. . .')
        if form.is_valid():
            # check rotate logic if we can't get here.
            print('Form is valid.')
            print(form.cleaned_data)
            resize = form.cleaned_data.get('resize') / 100
            avatar.resize((int(ava_w*resize), int(ava_h*resize)), resample=Image.NEAREST).save(temp_path)
            # Set avatar variable to temp_avatar file.
            avatar = Image.open(temp_path)
            print('Resized to x{}'.format(str(resize)))  # resize should be an int?
            rotate = form.cleaned_data.get('rotation')  # rotate is a str?
            print('Rotate var is a: {}'.format(type(rotate)))
            if rotate == 'vertical':
                avatar.transpose(Image.FLIP_TOP_BOTTOM).save(temp_path)
            elif rotate == 'horizontal':
                avatar.transpose(Image.FLIP_LEFT_RIGHT).save(temp_path)
            else:
                avatar.rotate(int(rotate)).save(temp_path)
                print('Rotated by {} degrees.'.format(rotate))
            if form.cleaned_data.get('blackwhite'):
                avatar = Image.open(temp_path)
                avatar.convert(mode='L').save(temp_path)
                print('Greyscaled!')
            print('Continue editing.  Send ava path back to top of view.')
            return redirect('accounts:transformphoto', pk=pk)

    form = forms.PhotoEditForm()
    context = {
        'form': form,
        'user': target_user,
        'temp_path': temp_path
    }
    return render(request, 'accounts/photo_edit_form.html', context)


@login_required
def avatar_confirm_view(request, pk):
    target_user = User.objects.get(id=pk)
    if identify(request, target_user):
        return HttpResponseRedirect(reverse('home'))
    avatype = target_user.avatar.path[-4:]
    temp_path = 'media/avatars/{}{}'.format(
        target_user.username,
        avatype
    )
    avatar = Image.open(temp_path)
    print(avatar)
    avatar.save(target_user.avatar.path)
    target_user.save()
    return redirect('accounts:photo', pk=pk)
