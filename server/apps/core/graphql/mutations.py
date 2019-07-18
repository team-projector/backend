import graphene
from rest_framework.exceptions import PermissionDenied

from apps.core.graphql.security.mixins.mutation import AuthMutation
from apps.core.graphql.security.permissions import AllowAuthenticated


class BaseMutation(AuthMutation,
                   graphene.Mutation):
    permission_classes = (AllowAuthenticated,)

    class Meta:
        abstract = True

    @classmethod
    def mutate(cls, root, info, **kwargs):
        cls.check_premissions(root, info, **kwargs)

        return cls.do_mutate(root, info, **kwargs)

    @classmethod
    def check_premissions(cls, root, info, **kwargs):
        if not cls.has_permission(root, info, **kwargs):
            raise PermissionDenied()

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        raise NotImplementedError
