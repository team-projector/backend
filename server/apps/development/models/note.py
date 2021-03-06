from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _
from jnt_admin_tools.db.fields import GenericForeignKey
from jnt_django_toolbox.models.fields import EnumField

from apps.users.models import User


class NoteType(models.TextChoices):
    """Note types choices."""

    TIME_SPEND = "TIME_SPEND", _("CH__TIME_SPEND")  # noqa: WPS115
    RESET_SPEND = "RESET_SPEND", _("CH__RESET_SPEND")  # noqa: WPS115
    MOVED_FROM = "MOVED_FROM", _("CH__MOVED_FROM")  # noqa: WPS115
    COMMENT = "COMMENT", _("CH__COMMENT")  # noqa: WPS115


NOTE_TYPE_MAX_LENGTH = 20


class Note(models.Model):
    """
    The milestone model.

    Fill from Gitlab when loading issues or merge requests.
    """

    class Meta:
        verbose_name = _("VN__NOTE")
        verbose_name_plural = _("VN__NOTES")
        ordering = ("-created_at",)

    object_id = models.IntegerField()

    gl_id = models.PositiveIntegerField(
        unique=True,
        verbose_name=_("VN__GITLAB_ID"),
        help_text=_("HT__GITLAB_ID"),
    )

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    body = models.TextField()

    type = EnumField(  # noqa: WPS125
        enum=NoteType,
        verbose_name=_("VN__TYPE"),
        help_text=_("HT__TYPE"),
    )

    data = models.JSONField(encoder=DjangoJSONEncoder)  # noqa: WPS110

    content_object = GenericForeignKey()

    content_type = models.ForeignKey(ContentType, models.CASCADE)

    user = models.ForeignKey(  # noqa: CCE001
        User,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("VN__USER"),
        help_text=_("HT__USER"),
    )

    def __str__(self):
        """Returns object string representation."""
        return "{0} [{1}]: {2}".format(
            self.user,
            self.created_at,
            self.get_type_display(),
        )
