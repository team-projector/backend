# -*- coding: utf-8 -*-

from graphene_django.views import GraphQLView
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from apps.core.graphql.security.authentication import TokenAuthentication


class ApiGraphQLView(GraphQLView):
    """Api GraphQL View."""

    def parse_body(self, request):
        """Parse body."""
        if isinstance(request, Request):
            return request.data

        return super().parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        """Main entry point for a request-response process."""
        view = super().as_view(*args, **kwargs)
        view = permission_classes((AllowAny,))(view)
        view = authentication_classes([TokenAuthentication])(view)
        view = api_view(["GET", "POST"])(view)
        return view
