import graphene
import json
from django.contrib.auth import REDIRECT_FIELD_NAME
from social_core.actions import do_complete
from social_django.views import _do_login

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowAny
from apps.users.graphql.types import TokenType
from apps.users.models import Token
from .utils import psa


class CompleteGitlabAuthMutation(BaseMutation):
    permission_classes = (AllowAny,)

    token = graphene.Field(TokenType)

    class Arguments:
        code = graphene.String(required=True)
        state = graphene.String(required=True)

    @classmethod
    def do_mutate(cls, root, info, code, state):
        request = psa(info.context)
        request.backend.set_data(code=code, state=state)

        response = do_complete(
            request.backend,
            _do_login,
            user=None,
            redirect_name=REDIRECT_FIELD_NAME,
            request=request
        )

        token_key = json.loads(response.content).get('token')

        return CompleteGitlabAuthMutation(
            token=Token.objects.get(key=token_key)
        )
