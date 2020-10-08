import graphene
from jnt_django_graphene_toolbox.mutations import BaseMutation


class LogoutMutation(BaseMutation):
    """Logout mutation."""

    status = graphene.String()

    @classmethod
    def do_mutate(cls, root, info):  # noqa: WPS110
        """After successful logout return "success"."""
        info.context.auth.delete()

        return LogoutMutation(status="success")
