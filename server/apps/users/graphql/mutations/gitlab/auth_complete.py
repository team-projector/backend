import graphene
from django.contrib.auth import REDIRECT_FIELD_NAME
from social_core.actions import do_complete

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowAny
from apps.users.graphql.types import TokenType
from apps.users.services.auth import login_user
from .utils import psa

from social_django.views import _do_login


class AuthCompleteMutation(BaseMutation):
    permission_classes = (AllowAny,)

    ok = graphene.Boolean()

    class Arguments:
        code = graphene.String(required=True)
        state = graphene.String(required=True)

    @classmethod
    def do_mutate(cls, root, info, code, state):
        request = psa(info.context)

        do_complete(
            request.backend,
            _do_login,
            user=None,
            redirect_name=REDIRECT_FIELD_NAME,
            request=request
        )

        return AuthCompleteMutation(
            ok=True
        )
