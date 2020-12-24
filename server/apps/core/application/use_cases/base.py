import abc
from typing import Generic, TypeVar

TInputDto = TypeVar("TInputDto")
TOutputDto = TypeVar("TOutputDto")


class BaseUseCase(Generic[TInputDto, TOutputDto], abc.ABC):
    """Base class for use cases."""

    @abc.abstractmethod
    def execute(self, input_dto: TInputDto) -> None:
        """Main logic here."""
