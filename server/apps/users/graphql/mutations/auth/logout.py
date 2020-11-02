import graphene
from jnt_django_graphene_toolbox.mutations import BaseMutation

from apps.users.services.user.auth import logout_user


class LogoutMutation(BaseMutation):
    """Logout mutation."""

    status = graphene.String()

    @classmethod
    def do_mutate(cls, root, info):  # noqa: WPS110
        """After successful logout return "success"."""
        logout_user(info.context)

        return cls(status="success")
