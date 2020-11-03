from typing import Dict, Optional

import graphene
from django.contrib.auth import REDIRECT_FIELD_NAME
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAny
from rest_framework import serializers
from social_core.actions import do_complete
from social_django.views import _do_login  # noqa: WPS450

from apps.users.graphql.mutations.helpers.auth import page_social_auth
from apps.users.graphql.types import TokenType
from apps.users.models import Token


class InputSerializer(serializers.Serializer):
    """InputSerializer."""

    code = serializers.CharField()
    state = serializers.CharField()


class CompleteGitlabAuthMutation(SerializerMutation):
    """Complete login mutation after redirection from Gitlab."""

    class Meta:
        serializer_class = InputSerializer

    permission_classes = (AllowAny,)

    token = graphene.Field(TokenType)

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data: Dict[str, str],
    ) -> "CompleteGitlabAuthMutation":
        """After successful login return class with token."""
        request = page_social_auth(info.context)
        request.backend.set_data(**validated_data)

        complete_result = do_complete(
            request.backend,
            _do_login,
            user=None,
            redirect_name=REDIRECT_FIELD_NAME,
            request=request,
        )
        token = None
        if isinstance(complete_result, Token):
            token = complete_result

        return cls(token=token)
