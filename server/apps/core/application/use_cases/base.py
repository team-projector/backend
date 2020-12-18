import abc

from apps.core.application.use_cases import BasePresenter


class BaseUseCase(abc.ABC):
    """Base class for use cases."""

    def __init__(self, presenter: BasePresenter) -> None:
        """Initializing."""
        self.presenter = presenter

    @abc.abstractmethod
    def execute(self, input_dto) -> None:
        """Main logic here."""
