import graphene
from jnt_django_graphene_toolbox.mutations import BaseMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAny

from apps.users.graphql.types import TokenType
from apps.users.services.user.login import login_user


class LoginMutation(BaseMutation):
    """Login mutation returns token."""

    class Arguments:
        login = graphene.String(required=True)
        password = graphene.String(required=True)

    permission_classes = (AllowAny,)

    token = graphene.Field(TokenType)

    @classmethod
    def do_mutate(cls, root, info, login, password):  # noqa: WPS110
        """After successful login return token."""
        token = login_user(login, password, info.context)

        return LoginMutation(token=token)
