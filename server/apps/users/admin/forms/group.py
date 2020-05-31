# -*- coding: utf-8 -*-

from admin_tools.fields import PermissionSelectMultipleField
from django.contrib.auth.models import Group

from apps.core.admin.forms import BaseModelForm


class GroupAdminForm(BaseModelForm):
    """Show form of Group model with select multiple field."""

    class Meta:
        model = Group
        fields = "__all__"

    permissions = PermissionSelectMultipleField(required=False)
