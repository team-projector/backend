from contextlib import suppress

from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.contenttypes.models import ContentType
from jnt_admin_tools.admin.content_type import BaseContentTypeAdmin

with suppress(NotRegistered):
    admin.site.unregister(ContentType)


@admin.register(ContentType)
class ContentTypeAdmin(BaseContentTypeAdmin):
    """Register content type admin."""
