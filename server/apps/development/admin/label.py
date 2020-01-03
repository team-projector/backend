# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.core.admin.base import BaseModelAdmin
from apps.development.models import Label

COLOR_TEMPLATE = """
                <div style="float: left;"> {color} </div>
                <div style="background-color: {color};
                float: left;
                margin-left: 6px;
                width: 14px;
                height: 14px;
                border: 1.1px solid black;"> </div>
               """


@admin.register(Label)
class LabelAdmin(BaseModelAdmin):
    """A class representing Label model for admin dashboard."""

    list_display = ("title", "color_square")
    search_fields = ("title",)

    fieldsets = (
        (None, {
            "fields": ("title", "color_square"),
        }),
    )

    readonly_fields = ("title", "color_square")

    @mark_safe
    def color_square(self, label):
        """Show current label with colored square near."""
        return COLOR_TEMPLATE.format(
            color=label.color,
        )

    color_square.short_description = "color"
