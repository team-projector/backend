# -*- coding: utf-8 -*-

from django.contrib.auth.mixins import LoginRequiredMixin
from graphene_django.views import GraphQLView


class PlaygroundGraphQLView(LoginRequiredMixin, GraphQLView):
    """Playground GraphQL View."""
