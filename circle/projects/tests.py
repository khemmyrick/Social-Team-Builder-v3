from django.test import TestCase
from django.utils import timezone

from accounts import models as amodels
from projects import forms
from projects import models as pmodels
from projects import serializers

# May have to import User from settings...?
# May have to doublecheck syntax for import from accounts app.


# Circle Projects Tests
class ModelSetUp(object):
    def setUp(self):
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
            description='Project1 Description',
            creator=self.user1,
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
            status=True
        )
        self.appl1.save()


class ViewSetUp(object):
    pass


class ProjectModelTests(ModelSetUp, TestCase):
    '''Project model tests.'''
    # CURRENTLY OK!
    def test_applicant_creation(self):
        self.assertEqual(self.appl1.user, self.user1)
        self.assertEqual(self.appl1.position, self.posi1)
        self.assertLessEqual(self.appl1.applied, timezone.now())
        self.assertEqual(self.appl1.status, True)

    def test_position_creation(self):
        self.assertEqual(self.posi1.name, 'Job1')
        self.assertEqual(self.posi1.project, self.proj1)
        self.assertEqual(self.posi1.user, self.user1)
        self.assertIn(self.skill1, self.posi1.skills.all())


    def test_project_creation(self):
        self.assertEqual(self.proj1.name, 'Project 1')
        self.assertNotEqual(self.proj1.name, self.proj2.name)
        self.assertEqual(self.proj1.creator.username, 'User1')


class ProjectSerializersTests(ModelSetUp, TestCase):
    # CURRENTLY OK!
    def test_project_serializer(self):
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
        skill_serializer = serializers.SkillSerializer(
            instance=self.skill1
        )
        self.assertEqual(set(skill_serializer.data.keys()),
                         set(['name']))
        self.assertEqual(skill_serializer.data['name'], self.skill1.name)


class ProjectFormTests(TestCase):
    def test_skill_form(self):
        form_data = {'name': 'name'}
        form = forms.SkillForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_position_form(self):
        form_data = {
            'name': 'name',
            'description': 'description',
            'time': '5 hours / day'
        }
        form = forms.PositionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_project_form(self):
        form_data = {
            'name': 'name',
            'url': 'https://www.example.com',
            'description': 'description',
            'requirements': 'requirements',
            'time': '25 hours / week'
        }
        form = forms.ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_project_create_form(self):
        form_data = {
            'name': 'name',
            'url': 'https://www.example.com',
            'description': 'description',
            'requirements': 'requirements',
            'time': '25 hours / week'
        }
        form = forms.ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_base_skill_formset(self):
        pass


class ProjectViewTests(ViewSetUp, ModelSetUp, TestCase):
    pass
