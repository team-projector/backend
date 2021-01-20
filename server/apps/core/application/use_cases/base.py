import abc
import dataclasses
from typing import TypeVar

from apps.core.application.errors import InvalidInputApplicationError

TInputDto = TypeVar("TInputDto")
TOutputDto = TypeVar("TOutputDto")


class Empty:
    """Represents not filled value."""

    def __deepcopy__(self, memodict):
        """No copy, but himself."""
        return self


empty = Empty()


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
        to_validate = {
            data_key: data_value
            for data_key, data_value in dataclasses.asdict(input_data).items()
            if data_value != empty
        }

        validator = validator_class(data=to_validate)
        if not validator.is_valid():
            raise InvalidInputApplicationError(validator.errors)

        return validator.validated_data
