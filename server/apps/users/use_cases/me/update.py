from dataclasses import dataclass
from typing import Dict, Union

from rest_framework import serializers

from apps.core.application.use_cases import (
    BasePresenter,
    BaseUseCase,
    Empty,
    empty,
)
from apps.users.models import User


@dataclass(frozen=True)
class MeUpdateData:
    """Update issue data."""

    name: Union[str, Empty] = empty
    email: Union[str, Empty] = empty
    gl_token: Union[str, Empty] = empty


@dataclass(frozen=True)
class InputDto:
    """Update issue input dto."""

    user: User
    data: MeUpdateData  # noqa: WPS110


@dataclass(frozen=True)
class OutputDto:
    """Update issue output dto."""

    user: User


class InputDtoValidator(serializers.Serializer):
    """InputSerializer."""

    class Meta:
        model = User

    name = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    email = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    gl_token = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )


class UseCase(BaseUseCase):
    """Usecase for updating issues."""

    def __init__(self, presenter: BasePresenter):
        """Initialize."""
        self._presenter = presenter

    def execute(self, input_dto: InputDto) -> None:
        """Main logic here."""
        validated_data = self.validate_input(input_dto.data, InputDtoValidator)

        user = input_dto.user
        self._update_user(user, validated_data)

        user.save()

        self._presenter.present(OutputDto(user=user))

    def _update_user(
        self,
        user: User,
        validated_data: Dict[str, Union[str, Empty]],
    ) -> None:
        name = validated_data.get("name", empty)
        if name != empty:
            user.name = name or ""

        email = validated_data.get("email", empty)
        if email != empty:
            user.email = email or ""

        gl_token = validated_data.get("gl_token", empty)
        if gl_token != empty:
            user.gl_token = gl_token or ""
