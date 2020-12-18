from typing import Optional, Type, Union

from graphql import GraphQLError, ResolveInfo
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from jnt_django_graphene_toolbox.mutations.serializer import (
    SerializerMutationOptions,
)
from rest_framework.serializers import Serializer

from apps.core.application.errors import BaseApplicationError
from apps.core.application.use_cases import BaseUseCase
from apps.core.graphql.errors import ApplicationGraphQLError
from apps.core.graphql.mutations import MutationPresenter


class UseCaseMutationOptions(SerializerMutationOptions):
    """Use case mutation options."""

    use_case_class: Optional[Type[BaseUseCase]] = None
    serializer_class: Optional[Type[Serializer]] = None
    permission_classes = None


class BaseUseCaseMutation(SerializerMutation):
    """Base class for mutations based on use cases."""

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        permission_classes=None,
        use_case_class=None,
        _meta=None,
        **options,
    ):
        """Initialize class with meta."""
        if not _meta:
            _meta = UseCaseMutationOptions(cls)  # noqa: WPS122

        _meta.use_case_class = use_case_class
        _meta.permission_classes = permission_classes
        super().__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def check_premissions(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **input,  # noqa: WPS125
    ) -> None:
        """Check permissions."""
        has_permission = all(
            perm().has_mutation_permission(root, info, **input)
            for perm in cls._meta.permission_classes
        )

        if not has_permission:
            raise GraphQLPermissionDenied

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> Union["BaseUseCaseMutation", GraphQLError]:
        """Overrideable mutation operation."""
        presenter = MutationPresenter()
        use_case = cls._meta.use_case_class(presenter)

        try:
            use_case.execute(cls.get_input_dto(root, info, validated_data))
        except BaseApplicationError as err:
            return ApplicationGraphQLError(err)
        else:
            return cls.present(root, info, presenter.get_presented_data())

    @classmethod
    def present(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110,
        output_dto,
    ) -> "BaseUseCaseMutation":
        """Presents response."""
        raise NotImplementedError

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ):
        """Stub for getting usecase input dto."""
