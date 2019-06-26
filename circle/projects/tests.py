from django.test import RequestFactory, TestCase
from django.template.response import TemplateResponse
from django.utils import timezone

from accounts import models as amodels
from projects import forms
from projects import models as pmodels
from projects import serializers
from projects import views


# Circle Projects Tests
class ModelSetUp(object):
    """Preset objects for model tests."""
    def setUp(self):
        self.factory = RequestFactory()

        # 1. Account Models
        # User Models
        self.user1 = amodels.User(
            email='user1@example.com',
            username='User1',
            display_name='User_1',
            bio='User1 Bio',
            avatar=None,
            is_staff=True,
            is_active=True,
            password='project12'
        )
        self.user1.save()
        self.skill1 = self.user1.skills.create(name='Skill1')
        self.skill1.save()

        self.user2 = amodels.User(
            email='user2@example.com',
            username='User2',
            display_name='User_2',
            bio='User2 Bio',
            avatar=None,
            is_staff=False,
            is_active=True,
            password='project12'
        )
        self.user2.save()

        self.user3 = amodels.User(
            email='user3@example.com',
            username='User3',
            display_name='User 3',
            bio='User3 Bio',
            avatar=None,
            is_staff=False,
            is_active=True,
            password='project12'
        )
        self.user3.save()

        # Additional Skill Models
        self.skill2 = pmodels.Skill(
            name='Skill2',
        )
        self.skill2.save()
        self.user2.skills.add(
            self.skill1,
            self.skill2
        )

        self.skill3 = pmodels.Skill(
            name='Skill3',
        )
        self.skill3.save()
        self.user3.skills.add(
            self.skill1,
            self.skill2,
            self.skill3
        )

        # 2. Project Models
        # Project Models
        # With no name default should either be "Project 1" or "Project 0".
        self.proj1 = pmodels.Project(
            name='Project 1',
            description='## Project1 Description',
            creator=self.user2,
            requirements='req1'
        )
        self.proj1.save()

        self.proj2 = pmodels.Project(
            name='Project 2',
            description='Project2 Description',
            creator=self.user1,
            requirements='req2'
        )
        self.proj2.save()

        # Position Models
        self.posi1 = pmodels.Position(
            name='Job1',
            description='Job1desc',
            project=self.proj1,
            user=self.user1,
            filled=True,
            time='5days/week'
        )
        self.posi1.save()
        self.posi1.skills.add(
            self.skill1,
            self.skill2,
            self.skill3
        )
        self.posi1.save()

        # Applicant Models
        self.appl1 = pmodels.Applicant(
            user=self.user1,
            position=self.posi1,
            status='a'
        )
        self.appl1.save()


class ProjectModelTests(ModelSetUp, TestCase):
    '''Project model tests.'''
    def test_applicant_creation(self):
        """Check that created applicant contains expected data."""
        self.assertEqual(self.appl1.user, self.user1)
        self.assertEqual(self.appl1.position, self.posi1)
        self.assertLessEqual(self.appl1.applied, timezone.now())
        self.assertEqual(self.appl1.status, 'a')

    def test_position_creation(self):
        """Check that created position contains expected data."""
        self.assertEqual(self.posi1.name, 'Job1')
        self.assertEqual(self.posi1.project, self.proj1)
        self.assertEqual(self.posi1.user, self.user1)
        self.assertIn(self.skill1, self.posi1.skills.all())

    def test_project_creation(self):
        """Check that created project contains expected data."""
        self.assertEqual(self.proj1.name, 'Project 1')
        self.assertNotEqual(self.proj1.name, self.proj2.name)
        self.assertEqual(self.proj1.creator.username, 'User2')

    def test_skill_creation(self):
        """Check that created skill contains expected data."""
        self.assertEqual(self.skill1.name, 'Skill1')
        self.assertTrue(self.skill1.users.all())


class ProjectSerializersTests(ModelSetUp, TestCase):
    """Project serializer tests."""
    def test_project_serializer(self):
        """Create project serializer.

        Check that serializer contains expected key and value.
        """
        project_serializer = serializers.ProjectSerializer(
            instance=self.proj1
        )
        self.assertEqual(set(project_serializer.data.keys()),
                         set(['name',
                              'description',
                              'creator',
                              'requirements',
                              'active',
                              'url',
                              'time']))
        self.assertEqual(
            project_serializer.data['name'],
            self.proj1.name
        )

    def test_position_serializer(self):
        """Create position serializer.

        Check that serializer contains expected key and value.
        """
        position_serializer = serializers.PositionSerializer(
            instance=self.posi1
        )
        self.assertEqual(set(position_serializer.data.keys()),
                         set(['name',
                              'description',
                              'filled',
                              'project',
                              'user',
                              'skills',
                              'time',
                              'active']))
        self.assertEqual(
            position_serializer.data['name'],
            self.posi1.name
        )

    def test_applicant_serializer(self):
        """Create applicant serializer.

        Check that serializer contains expected key and value.
        """
        applicant_serializer = serializers.ApplicantSerializer(
            instance=self.appl1
        )
        self.assertEqual(set(applicant_serializer.data.keys()),
                         set(['user',
                              'position',
                              'status']))
        self.assertEqual(
            applicant_serializer.data['status'],
            str(self.appl1.status)
        )

    def test_skill_serializer(self):
        """Create skill serializer.

        Check that serializer contains expected key and value.
        """
        skill_serializer = serializers.SkillSerializer(
            instance=self.skill1
        )
        self.assertEqual(set(skill_serializer.data.keys()),
                         set(['name']))
        self.assertEqual(skill_serializer.data['name'], self.skill1.name)


class ProjectFormTests(ModelSetUp, TestCase):
    """Project form tests."""
    def test_skill_form(self):
        """Tests skill form.

        Creates a form with sample skill data.
        Checks that form is valid and contains expected value.
        """
        form_data = {'name': 'name'}
        form = forms.SkillForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual('name', form.cleaned_data.get('name'))

    def test_position_form(self):
        """Tests position form.

        Creates a form with sample position data.
        Checks that form is valid and contains expected value.
        """
        form_data = {
            'name': 'name',
            'description': 'description',
            'time': '5 hours / day'
        }
        form = forms.PositionForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual('5 hours / day', form.cleaned_data.get('time'))

    def test_project_form(self):
        """Tests project form.

        Creates a form with sample project data.
        Checks that form is valid and contains expected value.
        """
        form_data = {
            'name': 'name',
            'url': 'https://www.example.com',
            'description': 'description',
            'requirements': 'requirements',
            'time': '25 hours / week'
        }
        form = forms.ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            'https://www.example.com',
            form.cleaned_data.get('url')
        )

    def test_project_create_form(self):
        """Tests project form.

        Creates a form with sample project data.
        Checks that form is valid and contains expected value.
        Checks that form contains valid model data.
        """
        form_data = {
            'name': 'name',
            'url': 'https://www.example.com',
            'description': 'description',
            'creator': self.user1,
            'requirements': 'requirements',
            'time': '25 hours / week'
        }
        form = forms.ProjectCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        project = pmodels.Project(
            name=form_data['name'],
            url=form_data['url'],
            description=form_data['description'],
            creator=form_data['creator'],
            requirements=form_data['requirements'],
            time=form_data['time']
        )
        project.save()
        self.assertTrue(pmodels.Project.objects.get(time='25 hours / week'))


class ProjectViewTests(ModelSetUp, TestCase):
    """Project view tests."""
    def test_project_detail_view(self):
        """Tests project details view.

        Use RequestFactory to make a request for the view.
        Check that view's response contains expected status code.
        Check that template response contains expected content.
        """
        request = self.factory.get('v3/projects/1/')
        request.user = self.user1
        response = views.project_detail_view(request, 1)
        # Response from server to client.
        self.assertEqual(response.status_code, 200)
        context = {
            'project': self.proj1,
            'applicants': [self.appl1]
        }
        template_response = TemplateResponse(
            request,
            'projects/project_detail.html',
            context)
        template_response.render()
        # Response rendered from actual template.
        self.assertIn(
            '<h2>Project1 Description</h2>',
            str(template_response.content)
        )

    def test_position_detail_view(self):
        """Tests position details view.

        Use RequestFactory to make a request for the view.
        Check that view's response contains expected status code.
        Check that template response contains expected content.
        """
        request = self.factory.get('v3/projects/1/position/1')
        request.user = self.user2
        response = views.position_detail_view(request, 1, 1)
        self.assertEqual(response.status_code, 200)
        applicants = request.user.applicants.filter(position=self.posi1)
        context = {
            'position': self.posi1,
            'applicants': applicants
        }
        template_response = TemplateResponse(
            request,
            'projects/position_detail.html',
            context
        )
        template_response.render()
        self.assertIn('Job1desc', str(template_response.content))
