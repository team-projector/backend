from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from jnt_admin_tools.db.fields import GenericForeignKey
from jnt_django_toolbox.models.fields import BitField

from apps.core.models.mixins import Timestamps


class ProjectMemberRole(models.TextChoices):
    """Project member role choices."""

    DEVELOPER = "DEVELOPER", _("CH__DEVELOPER")  # noqa: WPS115
    MANAGER = ("MANAGER", _("CH__MANAGER"))  # noqa: WPS115
    CUSTOMER = "CUSTOMER", _("CH__CUSTOMER")  # noqa: WPS115


PROJECT_MEMBER_ROLE_MAX_LENGTH = 20


class ProjectMember(Timestamps):
    """The project member model."""

    class Meta:
        verbose_name = _("VN__PROJECT_MEMBER")
        verbose_name_plural = _("VN__PROJECT_MEMBERS")
        unique_together = ("user", "object_id", "content_type")
        ordering = ("user__login",)

    roles = BitField(flags=ProjectMemberRole.choices, default=0)

    object_id = models.PositiveIntegerField(null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)

    owner = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, models.CASCADE, null=True)
