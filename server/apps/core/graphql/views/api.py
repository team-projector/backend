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
    def parse_body(self, request):
        if isinstance(request, Request):
            return request.data

        return super().parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        view = permission_classes((AllowAny,))(view)
        view = authentication_classes([TokenAuthentication])(view)
        view = api_view(['GET', 'POST'])(view)
        return view
