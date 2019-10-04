# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.mutations import BaseMutation


class LogoutMutation(BaseMutation):
    """
    Logout mutation.
    """
    ok = graphene.Boolean()

    @classmethod
    def do_mutate(cls, root, info):
        """
        After successful logout return "ok".
        """
        info.context.auth.delete()

        return LogoutMutation(ok=True)
