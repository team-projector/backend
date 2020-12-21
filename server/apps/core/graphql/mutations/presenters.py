import abc
from typing import Dict, Generic, Optional, TypeVar

from apps.core.application.use_cases import BasePresenter

TOutputDto = TypeVar("TOutputDto")


class BaseMutationPresenter(
    Generic[TOutputDto],
    BasePresenter[TOutputDto],
    metaclass=abc.ABCMeta,
):
    """
    Presenter for using in mutation use cases.

    Workaround of graphene classes structure.
    """

    def __init__(self, mutation_class):
        """Initialize."""
        self.output_dto: Optional[TOutputDto] = None
        self._mutation_class = mutation_class

    def present(self, output_dto: TOutputDto) -> None:
        """Save output dto."""
        self.output_dto = output_dto

    def get_response(self):
        """Returns response."""
        return self._mutation_class(**self.get_response_data())

    def get_response_data(self) -> Dict[str, object]:
        """Returns response fields."""
        return {}
