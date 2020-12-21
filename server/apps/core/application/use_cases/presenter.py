import abc
from typing import Generic, TypeVar

TOutputDto = TypeVar("TOutputDto")


class BasePresenter(Generic[TOutputDto], abc.ABC):
    """Abstract class for all presenters."""

    @abc.abstractmethod
    def present(self, output_dto: TOutputDto) -> None:
        """Process output dto."""
