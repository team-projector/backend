from typing import Optional, TypeVar

from apps.core.application.use_cases import BasePresenter

TOutputDto = TypeVar("TOutputDto")


class MutationPresenter(BasePresenter):
    """
    Presenter for using in mutation use cases.

    Workaround of graphene classes structure.
    """

    def __init__(self):
        """Initialize."""
        self.output_dto: Optional = None

    def present(self, output_dto: TOutputDto) -> None:
        """Save output dto."""
        self.output_dto = output_dto
