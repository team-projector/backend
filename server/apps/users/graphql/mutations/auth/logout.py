import graphene
from jnt_django_graphene_toolbox.mutations import BaseMutation

from apps.users.services.user.auth import user_logout


class LogoutMutation(BaseMutation):
    """Logout mutation."""

    status = graphene.String()

    @classmethod
    def do_mutate(cls, root, info):  # noqa: WPS110
        """After successful logout return "success"."""
        user_logout(info.context)

        return cls(status="success")
