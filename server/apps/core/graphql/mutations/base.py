from typing import Optional

from graphene.types.mutation import MutationOptions
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations.base import (
    BaseMutation as _BaseMutation,
)


class BaseMutation(_BaseMutation):
    """A base class mutation."""

    @classmethod
    def __init_subclass_with_meta__(  # noqa: WPS211
        cls,
        auth_required=False,
        _meta=None,
        **options,
    ):
        """Initialize class with meta."""
        if not _meta:
            _meta = MutationOptions(cls)  # noqa: WPS122

        _meta.auth_required = auth_required
        super().__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def check_premissions(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,  # noqa: WPS125
    ) -> bool:
        """Check permissions."""
        user = info.context.user  # type: ignore
        if cls._meta.auth_required:
            return user.is_authenticated

        return True
