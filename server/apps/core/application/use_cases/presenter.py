import abc


class BasePresenter(abc.ABC):
    """Abstract class for all presenters."""

    @abc.abstractmethod
    def present(self, output_dto) -> None:
        """Process output dto."""

    @abc.abstractmethod
    def get_presented_data(self):
        """Return output dto in additional format."""


class EmptyPresenter(BasePresenter):
    """Presenter without any logic."""

    def present(self, output_dto) -> None:
        """Nothing."""

    def get_presented_data(self):
        """Empty data."""
