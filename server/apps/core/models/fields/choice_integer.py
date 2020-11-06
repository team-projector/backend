from django import forms


class ChoiceIntegerField(forms.ChoiceField):
    """Choice integer field."""

    def to_python(self, value):  # noqa: WPS110
        """Return an integer."""
        return int(value)
