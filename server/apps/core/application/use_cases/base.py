import abc
from typing import Generic, TypeVar

from apps.core.application.use_cases import BasePresenter

TInputDto = TypeVar("TInputDto")
TOutputDto = TypeVar("TOutputDto")


class BaseUseCase(Generic[TInputDto, TOutputDto], abc.ABC):
    """Base class for use cases."""

    def __init__(self, presenter: BasePresenter[TOutputDto]) -> None:
        """Initializing."""
        self.presenter = presenter

    @abc.abstractmethod
    def execute(self, input_dto: TInputDto) -> None:
        """Main logic here."""
