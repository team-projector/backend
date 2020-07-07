# -*- coding: utf-8 -*-

from jnt_django_graphene_toolbox.views import BaseApiGraphQLView
from rest_framework.permissions import AllowAny

from apps.core.graphql.security.authentication import TokenAuthentication


class ApiGraphQLView(BaseApiGraphQLView):
    """Api GraphQL View."""

    permission_classes = (AllowAny,)
    authentication_classes = (TokenAuthentication,)
