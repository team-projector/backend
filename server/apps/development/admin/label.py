# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.core.admin.base import BaseModelAdmin

from ..models import Label


@admin.register(Label)
class LabelAdmin(BaseModelAdmin):
    list_display = ('title', 'color_square')
    search_fields = ('title',)

    fieldsets = (
        (None, {
            'fields': ('title', 'color_square'),
        }),
    )

    readonly_fields = ('title', 'color_square')

    @mark_safe
    def color_square(self, obj):
        """
        Show current label with colored square.
        """
        return f"""
                <div style="float: left;"> {obj.color} </div>
                <div style="background-color: {obj.color};
                float: left;
                margin-left: 6px;
                width: 14px;
                height: 14px;
                border: 1.1px solid black;"> </div>
               """

    color_square.short_description = 'color'
