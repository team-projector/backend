from django.contrib.auth.models import Group
from jnt_admin_tools.fields import PermissionSelectMultipleField

from apps.core.admin.forms import BaseModelForm


class GroupAdminForm(BaseModelForm):
    """Show form of Group model with select multiple field."""

    class Meta:
        model = Group
        fields = "__all__"

    permissions = PermissionSelectMultipleField(required=False)
