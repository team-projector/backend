from apps.core.utils.mail import transform


def test_transform(assets):
    """Test transform html."""
    assert (
        transform(
            assets.open_file("raw_template.html", "r").read(),
        )
        == assets.open_file("raw_rendered_template.html", "r").read()
    )
