from django.contrib import admin

from .models import Applicant, Position, Project
# Register your models here.
admin.site.register(Applicant)
admin.site.register(Position)
admin.site.register(Project)
