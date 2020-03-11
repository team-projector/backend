# -*- coding: utf-8 -*-

from contextlib import suppress
from typing import Iterable

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.related import OneToOneRel
from django.urls import reverse
from django.utils.html import mark_safe

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.admin.filters import HasSalaryFilter
from apps.payroll.models import Payroll
from apps.users.admin.filters import UserFilter


@admin.register(Payroll)
class PayrollAdmin(BaseModelAdmin):
    """A class representing Payroll model for admin dashboard."""

    list_display = ("user", "created_by", "created_at", "sum")
    list_filter = (UserFilter, HasSalaryFilter)
    search_fields = ("user__login", "user__email")
    readonly_fields = ("inheritance",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "inheritance",
                    "created_by",
                    "sum",
                    "salary",
                    "user",
                ),
            },
        ),
    )

    def inheritance(self, payroll):
        """Get link to Bonus, Penalty etc."""
        for field in self._get_accessor_names(self.model):
            node = None

            with suppress(ObjectDoesNotExist):
                node = getattr(payroll, field)

            if node:
                return self._get_inheritance_link(node)

    def _get_inheritance_link(self, node) -> str:
        meta = node._meta  # noqa: WPS437

        url = reverse(
            "admin:{0}_{1}_change".format(meta.app_label, meta.model_name),
            args=[node.id],
        )

        return mark_safe(
            "<a href={0}>{1}: ".format(url, meta.model_name.capitalize())
            + "{0}</a>".format(node),
        )

    def _get_accessor_names(self, model) -> Iterable[str]:
        related_objects = [
            item
            for item in model._meta.get_fields()  # noqa: WPS437, WPS110
            if isinstance(item, OneToOneRel)
            and issubclass(item.field.model, model)
        ]

        return [rel.get_accessor_name() for rel in related_objects]
