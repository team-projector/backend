from apps.core.application.use_cases import BasePresenter


class MutationPresenter(BasePresenter):
    """
    Presenter for using in mutation use cases.

    Workaround of graphene classes structure.
    """

    def __init__(self):
        """Initialize."""
        self._output_dto = None

    def present(self, output_dto) -> None:
        """Save output dto."""
        self._output_dto = output_dto

    def get_presented_data(self):
        """Returns output dto."""
        return self._output_dto
