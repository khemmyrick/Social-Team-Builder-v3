from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from accounts.models import Skill


class Project(models.Model):
    name = models.CharField(
        max_length=150,
        default='Project {}'.format(str(id)),
        unique=True)
    url = models.URLField(max_length=255, blank=True)
    # max_length of CharField classes cannot exceed 255 in certain cases.
    description = MarkdownxField()
    # max_length of TextField CAN exceed 255.
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name="projects",
                                on_delete=models.PROTECT)
    requirements = models.CharField(max_length=255, blank=True)
    time = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    # Should project HAVE positions, rather than vice versa?
    # project.positions to query positions.

    def __str__(self):
        return self.name

    @property
    def formatted_markdown(self):
        return markdownify(self.description)


class Position(models.Model):
    '''As a user of the site, I should be able to specify
    the positions my project needs help in with a name,
    a description, and related skill.
    '''
    name = models.CharField(max_length=100)
    # Multiple projects should be able to have positions with identical names.
    # A single project should be able to have positions with identical names.
    # Editing a position should NOT spawn a duplicate.
    description = models.TextField(max_length=500, blank=True)
    filled = models.BooleanField(default=False)
    project = models.ForeignKey(Project,
                                related_name="positions",
                                on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="positions",
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True)
    # user field will be blank until position is filled
    skills = models.ManyToManyField(
        Skill,
        related_name='positions',
        blank=True
    )
    time = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return "{} for {}.".format(self.name, self.project.name)


class Applicant(models.Model):
    """
    Object for storing applicants to a specific project position.

    attrs:
        user: ForeignKey user who may apply to position.
        position: ForeignKey position user may apply for.
        status: bool indicating that the user hasn't been rejected/accepted.
        applied: time this object was created.
    """
    # Revisit on_delete options later.
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='applicants')
    position = models.ForeignKey(Position,
                                 on_delete=models.CASCADE,
                                 related_name='applicants')
    applied = models.DateTimeField(default=timezone.now)
    status = models.CharField(default='u', max_length=10)
    # status should be CHAR Field.  'a' = approved. 'r' = rejected. 'u' = processing.
    def __str__(self):
        if self.status is 'u':
            return "USER {} being considered for {}.".format(
                self.user.display_name,
                self.position.name
            )
        elif self.status is 'a':
            return "USER {} is our new {}".format(
                self.user.display_name,
                self.position.name
            )
        else:
            return "{} is invited to pursue other oppportunities.".format(
                self.user.display_name
            )

    class Meta:
        ordering = ('-applied',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'position'],
                name='unique_attempt'
            )
        ]
