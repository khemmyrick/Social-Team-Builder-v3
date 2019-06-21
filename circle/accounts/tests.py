from django.test import RequestFactory, TestCase
from django.template.response import TemplateResponse
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.core import mail

from accounts.models import User, UserManager
from accounts.serializers import UserSerializer
from accounts import forms, views

# Create your tests here.
class ModelSetUp(object):
    def setUp(self):
        # 1. Account Models
        # User Models
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='User1',
            password='project12'
        )
        self.user1.save()
        self.user1.bio = '## User1 Bio'
        self.user1.save()

        self.user2 = User.objects.create_superuser(
            email='user2@example.com',
            username='User2',
            display_name='User 2',
            password='project12'
        )
        self.user2.save()


class ViewSetUp(object):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='User1',
            password='project12'
        )
        self.user1.save()
        self.user1.bio = '## User1 Bio'
        self.user1.save()


class AccountModelTests(ModelSetUp, TestCase):
    '''Account model tests.'''
    # CURRENTLY OK!
    def test_user_creation(self):
        self.assertEqual(len(User.objects.all()), 2)
        self.assertEqual(self.user1.username, 'User1')
        self.assertLessEqual(self.user1.date_joined, timezone.now())
        self.assertTrue(self.user1.is_active)
        self.assertFalse(self.user1.is_staff)
        self.assertTrue(self.user2.is_staff)

    def test_send_email(self):
        self.user1.email_user('Subject here', 'Here is the message.',
            'test@example.com',
            fail_silently=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subject here')

    def test_user_str(self):
        self.assertEqual(self.user1.__str__(), self.user1.username)
        self.assertEqual(self.user2.__str__(), self.user2.display_name)
        self.assertEqual(self.user1.formatted_markdown, '<h2>User1 Bio</h2>')

    # def test_unique_constraint(self):
    #    with transaction.atomic():
    #        self.failed_user = User(
    #            email='user3@example.com',
    #            username='User3',
    #            display_name='User 3',
    #            bio='User3 Bio',
    #            avatar=None,
    #            is_staff=False,
    #            is_active=True,
    #            password='project12'
    #        )
    #    with self.assertRaises(IntegrityError):
    #        self.failed_user.save()
    #    # Test that creating a user with a pre-existing name raises IntegrityError
    #    # Test exceptions for all User model validators.

    def test_user_avatar(self):
        pass


class AccountViewTests(ViewSetUp, TestCase):
    def test_user_update_view(self):
        pass
        #request = views.user_update_view(pk=1)
        # user = self.user1
        
    def test_user_detail_view(self):
        request = self.factory.get('v3/accounts/1/')
        # Request sent from client to server...
        request.user = self.user1
        response = views.user_detail_view(request, 1)
        # Response from server to client.
        self.assertEqual(response.status_code, 200)
        context = {
            'user': request.user,
            'target_user': request.user,
            'skills': ''
        }
        template_response = TemplateResponse(
            request,
            'accounts/user_detail.html',
            context)
        template_response.render()
        # Response rendered from actual template.
        self.assertIn('<h2>User1 Bio</h2>', str(template_response.content))

    def test_log_out_view(self):
        request = self.factory.get('v3/accounts/logout/')
        request.user = self.user1
        print('User is: {}'.format(request.user))
        view = views.LogOutView.as_view()
        # request has no attribute "session"
        # response = view(request)
        # self.assertEqual(response.status_code, 200)


class AccountFormTests(TestCase):
    def test_user_form(self):
        form_data = {
            'display_name': 'Display Name',
            'bio': 'little did he know'
        }
        form = forms.UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_registration_form(self):
        form_data = {
            'email': 'example@example.com',
            'username': 'NewestUser',
            'password1': 'project12',
            'password2': 'project12'
        }
        form = forms.UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_bad_user_registration_form(self):
        form_data = {
            'email': 'exampleexamplecom',
            'username': 'NewestUser',
            'password1': 'project12',
            'password2': 'project14'
        }
        form = forms.UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        # self.assertRaises()
