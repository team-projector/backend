from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.db.mixins import Timestamps
from apps.core.models.db.utils import Choices
from apps.users.models import User


class ProjectMember(Timestamps):
    ROLE = Choices(
        ('developer', _('CH_DEVELOPER')),
        ('project_manager', _('CH_PM')),
        ('customer', _('CH_CUSTOMER')),
    )

    user = models.ForeignKey(
        User,
        models.CASCADE
    )

    role = models.CharField(
        choices=ROLE,
        max_length=20,
        verbose_name=_('VN__ROLE'),
        help_text=_('HT__ROLE')
    )

    owner = GenericForeignKey()
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        null=True
    )
    object_id = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = _('VN__PROJECT_MEMBER')
        verbose_name_plural = _('VN__PROJECT_MEMBERS')
        unique_together = ('user', 'role', 'object_id')
