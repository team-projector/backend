from django.utils.translation import gettext_lazy as _

from apps.core.admin.forms import BaseModelForm
from apps.development.models import TeamMember


class TeamMemberForm(BaseModelForm):
    """Base model form for team model."""

    class Meta:
        model = TeamMember
        fields = "__all__"

    def clean_roles(self):
        """Clean roles."""
        roles = self.cleaned_data.get("roles")
        if not roles:
            self.add_error(
                "roles",
                _("MSG__YOU_MUST_CHOOSE_AT_LEAST_ONE_ROLE"),
            )

        return roles
