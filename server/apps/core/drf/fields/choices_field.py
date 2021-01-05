from jnt_django_graphene_toolbox.serializers.fields.char import CharField
from rest_framework import serializers


class ChoicesField(CharField):
    """Custom choices field with validation."""

    def __init__(self, choices, **kwargs):
        """Initialization."""
        self._choices = choices

        kwargs["validators"] = [
            self._validate_choice,
        ]

        super().__init__(**kwargs)

    def _validate_choice(self, choice):
        """
        Validate choice.

        :param choice:
        """
        if choice and choice not in self._choices:
            raise serializers.ValidationError(
                "should be one of available choices: {0}".format(
                    ", ".join(self._choices),
                ),
            )
