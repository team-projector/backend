import abc
from typing import Generic, TypeVar

TOutputDto = TypeVar("TOutputDto")


class BasePresenter(Generic[TOutputDto], abc.ABC):
    """Abstract class for all presenters."""

    @abc.abstractmethod
    def present(self, output_dto: TOutputDto) -> None:
        """Process output dto."""

    @abc.abstractmethod
    def get_presented_data(self):
        """Return output dto in additional format."""


class EmptyPresenter(Generic[TOutputDto], BasePresenter[TOutputDto]):
    """Presenter without any logic."""

    def present(self, output_dto: TOutputDto) -> None:
        """Nothing."""

    def get_presented_data(self):
        """Empty data."""
