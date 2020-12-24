import graphene
from jnt_django_graphene_toolbox.mutations import BaseMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated

from apps.users.services.user.auth import logout_user


class LogoutMutation(BaseMutation):
    """Logout mutation."""

    class Meta:
        permission_classes = (AllowAuthenticated,)

    status = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):  # noqa: WPS110
        """After successful logout return "success"."""
        logout_user(info.context)

        return cls(status="success")
