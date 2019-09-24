# -*- coding: utf-8 -*-

from admin_tools.fields import PermissionSelectMultipleField
from django.contrib.auth.models import Group

from apps.core.admin.forms import BaseModelForm


class GroupAdminForm(BaseModelForm):
    permissions = PermissionSelectMultipleField(
        required=False,
    )

    class Meta:
        model = Group
        fields = '__all__'
