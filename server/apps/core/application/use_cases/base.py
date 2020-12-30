import abc
import dataclasses
from typing import TypeVar

from apps.core.application.errors import InvalidInputApplicationError

TInputDto = TypeVar("TInputDto")
TOutputDto = TypeVar("TOutputDto")


class BaseUseCase(abc.ABC):
    """Base class for use cases."""

    @abc.abstractmethod
    def execute(self, input_dto) -> None:
        """Main logic here."""

    def validate_input(self, input_data, validator_class):
        """
        Validate input data.

        Raise exception if data is invalid.
        """
        validator = validator_class(data=dataclasses.asdict(input_data))
        if not validator.is_valid():
            raise InvalidInputApplicationError(validator.errors)

        return validator.validated_data
