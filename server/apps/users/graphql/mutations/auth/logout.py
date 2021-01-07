import graphene

from apps.core import injector
from apps.core.graphql.mutations.base import BaseMutation
from apps.users.services.auth.logout import LogoutInputDto, LogoutService


class LogoutMutation(BaseMutation):
    """Logout mutation."""

    class Meta:
        auth_required = True

    status = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):  # noqa: WPS110
        """After successful logout return "success"."""
        service = injector.get(LogoutService)
        service.execute(
            LogoutInputDto(
                token=info.context.auth,
            ),
        )

        return cls(status="success")
