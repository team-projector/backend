from model_utils import Choices as ModelChoices


class Choices(ModelChoices):
    def __eq__(self, other):
        if isinstance(other, (tuple, list)) and self._doubles == list(other):
            return True

        return super().__eq__(other)

    def keys(self):
        return [choice[0] for choice in self._doubles]
