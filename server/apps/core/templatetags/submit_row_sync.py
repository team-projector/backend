from django import template
from django.contrib.admin.templatetags.admin_modify import submit_row as original_submit_row
from django.contrib.admin.templatetags.base import InclusionAdminNode


register = template.Library()


def submit_row_update(context):
    ctx = original_submit_row(context)
    ctx.update({
        'show_force_sync': True
    })
    return ctx


@register.tag(name='submit_row_sync')
def submit_row_tag(parser, token):
    return InclusionAdminNode(parser, token, func=submit_row_update, template_name='submit_line_sync.html')
