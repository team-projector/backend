import graphene

from apps.users.graphql.types import TokenType
from apps.users.services.auth.login import login_user


class LoginMutation(graphene.Mutation):
    token = graphene.Field(TokenType)

    class Arguments:
        login = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, login, password):
        token = login_user(
            login,
            password,
            info.context
        )

        return LoginMutation(
            token=token
        )
