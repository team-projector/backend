from django.template.loader import get_template
from premailer import Premailer


def transform(html: str) -> str:
    """Transform html. Apply style to tags."""
    return Premailer(
        html,
        keep_style_tags=True,
        cssutils_logging_level="FATAL",
        strip_important=False,
    ).transform()


def render_email_html(template_name: str, context=None) -> str:
    """Render email html with transform styles."""
    context = context or {}
    context.setdefault("title", "")
    context.setdefault("style", "")
    return transform(get_template(template_name).render(context))
