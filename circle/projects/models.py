from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from accounts.models import Skill


class Project(models.Model):
    name = models.CharField(
        max_length=150,
        default='Project {}'.format(str(id)),
        unique=True)
    description = models.CharField(max_length=500, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name="projects",
                                on_delete=models.PROTECT)
    requirements = models.CharField(max_length=500, blank=True)
    # project.positions to query positions.

    def __str__(self):
        return self.name


class Position(models.Model):
    '''As a user of the site, I should be able to specify
    the positions my project needs help in with a name,
    a description, and related skill.
    '''
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    # related_skill
    # like UserPref in pugorugh, regulates who can apply.
    filled = models.BooleanField(default=False)
    project = models.ForeignKey(Project,
                                related_name="positions",
                                on_delete=models.CASCADE) 
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="positions",
                             on_delete=models.PROTECT,
                             blank=True,
                             null=True)
    # user field will be blank until position is filled
    skills = models.ManyToManyField(Skill)
    # skills = foreign key for skills required
    time = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Applicant(models.Model):
    # like UserDog in PugorUgh... new instance for each applicant.
    # when an applicant is selected, all applicant instances related to this specific position are destroyed.
    # when an applicant is rejected, keep that instance so that applicant cannot re-apply, until position is filled.
    # user applying = foreign key
    # position applied for = foreign key
    """
    Object for storing applicants to a specific project position.

    attrs:
        user: foreignkey user who may apply to position.
        position: foreignkey position user may apply for.
        status: bool indicating that the user has submitted application.
        applied: time this object was created.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='applicants')
    position = models.ForeignKey(Position,
                                 on_delete=models.CASCADE,
                                 related_name='applicants')
    applied = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True)
    # status becomes False if a candidate has been rejected.
    def __str__(self):
        if self.status is True:
            return "USER {} being considered for {}.".format(
                self.user.display_name,
                self.position
            )
        else:
            return "{} is invited to pursue other oppportunities.".format(
                self.user.display_name
            )

    class Meta:
        ordering = ('-applied',)
