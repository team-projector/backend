# -*- coding: utf-8 -*-

from model_utils import Choices as ModelChoices


class Choices(ModelChoices):
    """Choices."""

    def __eq__(self, other):
        """Equals "current" and "other" values. Returns boolean value."""
        if isinstance(other, (tuple, list)) and self._doubles == list(other):
            return True

        return super().__eq__(other)

    def keys(self):
        """Get list of keys."""
        return [
            choice[0]
            for choice in self._doubles
        ]
