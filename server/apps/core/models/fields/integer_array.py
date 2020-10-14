from django.contrib.postgres.forms import SimpleArrayField
from django.forms import IntegerField


class IntegerArrayField(SimpleArrayField):
    """IntegerArrayField handles for postgres ArrayField."""

    def __init__(self, max_value=None, min_value=None, **kwargs):
        """Inits ArrayField with a base of IntegerField."""
        super().__init__(
            base_field=IntegerField(max_value=max_value, min_value=min_value),
            **kwargs,
        )
