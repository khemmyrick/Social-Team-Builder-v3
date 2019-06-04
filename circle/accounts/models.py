from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
# Create your models here.

def user_directory_path(instance, filename):
    # file will be uploaded to media/accounts/<id>/<filename>
    return 'accounts/{0}/{1}'.format(instance.pk, filename)


class UserManager(BaseUserManager):
    def create_user(self, email, username, display_name=None, password=None):
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
        user = self.create_user(
            email,
            username,
            display_name,
            password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "{} skill".format(self.name)
    # users = models.ManyToManyField(User, blank=True)
    # skill.users = queuryset of all users with this skill.


class User(AbstractBaseUser, PermissionsMixin):
    # Yes, PermissionsMixin comes 2nd in the docs, so that's how we do it.
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=True)
    display_name = models.CharField(max_length=140, blank=True)
    # bio = models.CharField(max_length=999999999999999, blank=True, default="")
    bio = MarkdownxField()
    avatar = models.ImageField(blank=True, null=True,
                               upload_to=user_directory_path)
    # avatars upload to media/accounts/<user.id>/
    skills = models.ManyToManyField(Skill, related_name='users', blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # Reverse foreignkey/manytomany attributes:
    # user.skill_set = allows user to query skills
    # user.projects = queryset of projects this user created.
    # user.positions = queryset of positions this user holds/held.
    # user.applicants = queryset of positions currently being applied for.
    # storage = file_storage

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["display_name", "username"]
    # REQUIRED_FIELDS is what's sent to the create_superuser method
    # outside of the entry passed to USERNAME_FIELD (email) and password.

    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.display_name

    def get_long_name(self):
        return "{} (@{})".format(self.display_name, self.username)

    @property
    def formatted_markdown(self):
        return markdownify(self.bio)
