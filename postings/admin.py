from django.contrib import admin

from .models import Posting


# Make job postings available in Django's admin interface.
admin.site.register(Posting)