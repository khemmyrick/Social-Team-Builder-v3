from django.contrib import admin

# from markdownx.admin import MarkdownxModelAdmin

from .models import Applicant, Position, Project, Skill
# Register your models here.
admin.site.register(Applicant)
admin.site.register(Position)
admin.site.register(Project)
admin.site.register(
    Skill,
    # MarkdownxModelAdmin
)
