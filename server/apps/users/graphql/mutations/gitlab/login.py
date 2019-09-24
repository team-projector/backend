# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import REDIRECT_FIELD_NAME
from social_core.actions import do_auth

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowAny
from .utils import psa


class LoginGitlabMutation(BaseMutation):
    permission_classes = (AllowAny,)

    redirect_url = graphene.String()

    @classmethod
    def do_mutate(cls, root, info):
        request = psa(info.context)

        response = do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)

        return LoginGitlabMutation(
            redirect_url=response.url,
        )
