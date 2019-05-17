from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts import forms as acforms
from accounts import models as acmodels
from accounts import serializers as acserializers
from accounts import views as acviews
# from projects import forms as proforms
from projects import models as promodels
from projects import serializers as proserializers
from projects import views as proviews

# May have to import User from settings...?
# May have to doublecheck syntax for import from accounts app.


# Circle Projects Tests
class ModelSetUp(object):
    def setUp(self):
        # 1. Account Models
        # User Models
        self.user1 = acmodels.User(
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

        self.user2 = acmodels.User(
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

        self.user3 = acmodels.User(
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
        self.skill2 = acmodels.Skill(
            name='Skill2',
        )
        self.skill2.save()
        self.user2.skills.add(
            self.skill1,
            self.skill2
        )

        self.skill3 = acmodels.Skill(
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
        self.proj1 = promodels.Project(
            name='Project 1',
            description='Project1 Description',
            creator=self.user1,
            requirements='req1'
        )
        self.proj1.save()

        self.proj2 = promodels.Project(
            name='Project 2',
            description='Project2 Description',
            creator=self.user1,
            requirements='req2'
        )
        self.proj2.save()

        # Position Models
        self.posi1 = promodels.Position(
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
        self.appl1 = promodels.Applicant(
            user=self.user1,
            position=self.posi1,
            status=True
        )
        self.appl1.save()


class TemplateSetUp(object):
    pass


class ViewSetUp(object):
    pass


class AccountModelTests(ModelSetUp, TestCase):
    '''Account model tests.'''
    # CURRENTLY OK!
    def test_user_creation(self):
        self.assertEqual(self.user1.username, 'User1')
        self.assertNotEqual(self.user1.email, self.user2.email)
        self.assertLessEqual(self.user1.date_joined, timezone.now())

    def test_skill_creation(self):
        self.assertEqual(self.skill1.name, 'Skill1')
        self.assertNotEqual(self.skill1.name, self.skill2.name)
        self.assertIn(self.user1, self.skill1.users.all())
        self.assertIn(self.skill3, self.user3.skills.all())


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


class AccountFormTests(ModelSetUp, TestCase):
    def test_user_create_form(self):
        form_data = {
            'email': 'formtest@example.com',
            'username': 'FormTest',
            'password1': 'project12',
            'password2': 'project12'
        }
        ucf = acforms.UserCreateForm(data=form_data)
        self.assertTrue(ucf.is_valid())

    def test_user_create_form_bees(self):
        form_data = {
            'megabuster': '0101011',
            'email': 'formtest@example.com',
            'username': 'FormTest',
            'password1': 'project12',
            'password2': 'project12'
        }
        ucf = acforms.UserCreateForm(data=form_data)
        ucf.is_valid()
        # self.assertNotEqual(ucf.cleaned_data['megabuster'], '') # Should be true
        self.assertFalse(ucf.is_valid()) # SHOULD BE FALSE

    def test_user_update_form(self):
        form_data = {
            'display_name': 'Form Test',
            'bio': 'Lorem Ipsum Etceterus'
        }
        uuf = acforms.UserUpdateForm(data=form_data)
        uuf.is_valid()
        self.assertTrue(uuf.is_valid)
        self.assertEqual(uuf.cleaned_data['bio'], 'Lorem Ipsum Etceterus')
    
    def test_user_update_form_bees(self):
        pass

    def test_skill_form(self):
        form_data = {
            'name': 'Play Testing'
        }
        form = acforms.SkillForm(data=form_data)
        self.assertTrue(form.is_valid)


class AccountSerializersTests(ModelSetUp, TestCase):
    # CURRENTLY OK!
    def test_contains_expected_fields(self):
        user_serializer = acserializers.UserSerializer(
            instance=self.user1
        )
        skill_serializer = acserializers.SkillSerializer(
            instance=self.skill1
        )

        self.assertEqual(set(user_serializer.data.keys()),
                         set(['email',
                              'username',
                              'bio',
                              'display_name',
                              'is_staff',
                              'is_active',
                              'avatar',
                              'skills']))

        self.assertEqual(set(skill_serializer.data.keys()),
                         set(['name']))


class ProjectSerializersTests(ModelSetUp, TestCase):
    # CURRENTLY OK!
    def test_contains_expected_fields(self):
        project_serializer = proserializers.ProjectSerializer(
            instance=self.proj1
        )
        position_serializer = proserializers.PositionSerializer(
            instance=self.posi1
        )
        applicant_serializer = proserializers.ApplicantSerializer(
            instance=self.appl1
        )
        self.assertEqual(set(position_serializer.data.keys()),
                         set(['name',
                              'description',
                              'filled',
                              'project',
                              'user',
                              'skills',
                              'time']))

        self.assertEqual(set(project_serializer.data.keys()),
                         set(['name',
                              'description',
                              'creator',
                              'requirements']))

        self.assertEqual(set(applicant_serializer.data.keys()),
                         set(['user',
                              'position',
                              'status']))


class ProjectTemplateTests(TemplateSetUp, ViewSetUp, ModelSetUp, TestCase):
    pass


class AccountViewTests(ModelSetUp, TestCase):
    def test_sign_up_view(self):
        # FAIL!
        resp = self.client.get('/v3/accounts/signup/')
        # resp.context['name']
        self.assertEqual(resp.status_code, 200)
        # self.assertEqual(resp, 'notanequal')
        # self.assertTemplateUsed(resp, 'accounts/signup.html')
        # "No template used to render the response?"


class ProjectViewTests(ViewSetUp, ModelSetUp, TestCase):
    pass

