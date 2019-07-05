from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from projects.models import Skill
# Create your models here.


def user_directory_path(instance, filename):
    # file will be uploaded to media/accounts/<id>/<filename>
    return 'accounts/{0}/{1}'.format(instance.pk, filename)


class UserManager(BaseUserManager):
    def create_user(self, email, username, display_name=None, password=None):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("Users must have email address.")
        if display_name is None:
            display_name = username

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            display_name=display_name
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, display_name, password):
        """
        Create and save a user with the given username, email, display_name,
        and password. Set is_staff and is_superuser to True.
        """
        user = self.create_user(
            email,
            username,
            display_name,
            password
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User model."""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=True)
    display_name = models.CharField(max_length=140, blank=True)
    bio = MarkdownxField()
    avatar = models.ImageField(blank=True, null=True,
                               upload_to=user_directory_path)
    # avatars upload to media/accounts/<user.id>/<filename>
    skills = models.ManyToManyField(Skill, related_name='users', blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    notifications = models.TextField(default='')
    # Reverse foreignkey/manytomany attributes:
    # user.skill_set = allows user to query skills
    # user.projects = queryset of projects this user created.
    # user.positions = queryset of positions this user holds/held.
    # user.applicants = queryset of positions currently being applied for.
    # storage = file_storage

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["display_name", "email"]
    # REQUIRED_FIELDS is what's sent to the create_superuser method
    # outside of the entry passed to USERNAME_FIELD (email) and password.

    def __str__(self):
        if self.display_name:
            return self.display_name
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sends an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def add_notification(self, new_message):
        '''Stores a notification.'''
        self.notifications = self.notifications + ' | ' + new_message

    @property
    def formatted_markdown(self):
        """Converts markdown text characters into html tags."""
        return markdownify(self.bio)
