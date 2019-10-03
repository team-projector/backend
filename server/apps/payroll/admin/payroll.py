# -*- coding: utf-8 -*-

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.related import OneToOneRel
from django.urls import reverse
from django.utils.html import mark_safe

from apps.core.admin.base import BaseModelAdmin
from apps.users.admin.filters import UserFilter

from ..models import Payroll
from .filters import HasSalaryFilter


@admin.register(Payroll)
class PayrollAdmin(BaseModelAdmin):
    """
    A class representing Payroll model for admin dashboard.
    """
    list_display = ('user', 'created_by', 'created_at', 'sum')
    list_filter = (UserFilter, HasSalaryFilter)
    search_fields = ('user__login', 'user__email')
    readonly_fields = ('inheritance',)

    fieldsets = (
        (None, {
            'fields': ('inheritance', 'created_by', 'sum', 'salary', 'user'),
        }),
    )

    def inheritance(self, payroll):
        """
        Get link to Bonus, Penalty etc.
        """
        for field in self._get_accessor_names(self.model):
            node = None

            try:
                node = getattr(payroll, field)
            except ObjectDoesNotExist:
                pass

            if node:
                return self._get_inheritance_link(node)

    def _get_inheritance_link(self, node):
        url = reverse(
            f'admin:{node._meta.app_label}_{node._meta.model_name}_change',
            args=[node.id],
        )

        return mark_safe(
            f'<a href={url}>{node._meta.model_name.capitalize()}: '
            + f'{node}</a>',
        )

    @staticmethod
    def _get_accessor_names(model):
        related_objects = [
            item for item in model._meta.get_fields()
            if isinstance(
                item, OneToOneRel,
            ) and issubclass(
                item.field.model, model,
            )
        ]

        return [
            rel.get_accessor_name()
            for rel in related_objects
        ]
