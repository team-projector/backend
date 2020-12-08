from apps.core.utils.mail import render_email_html


def test_render_base_template(assets):
    """Test render base template html."""
    rendered = render_email_html("core/email/base.html")
    base_rendered = assets.open_file("base_rendered.html", "r").read()
    assert rendered.split() == base_rendered.split()
