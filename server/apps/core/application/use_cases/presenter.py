import abc


class BasePresenter(abc.ABC):
    """Abstract class for all presenters."""

    @abc.abstractmethod
    def present(self, output_dto) -> None:
        """Process output dto."""
