from django.contrib import admin
from django.contrib.auth import get_user_model

# from markdownx.admin import MarkdownxModelAdmin

# from .models import Skill
# Register your models here.

admin.site.register(get_user_model())
# admin.site.register(
#    Skill,
#    # MarkdownxModelAdmin
# )
