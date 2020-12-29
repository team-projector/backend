import abc
from typing import TypeVar

TInputDto = TypeVar("TInputDto")
TOutputDto = TypeVar("TOutputDto")


class BaseUseCase(abc.ABC):
    """Base class for use cases."""

    @abc.abstractmethod
    def execute(self, input_dto) -> None:
        """Main logic here."""
