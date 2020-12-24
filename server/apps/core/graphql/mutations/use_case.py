from typing import Optional, Type, Union

from graphql import GraphQLError, ResolveInfo
from jnt_django_graphene_toolbox.mutations import BaseSerializerMutation
from jnt_django_graphene_toolbox.mutations.serializer import (
    SerializerMutationOptions,
)
from rest_framework.serializers import Serializer

from apps.core.application.errors import BaseApplicationError
from apps.core.application.use_cases import BaseUseCase
from apps.core.graphql.errors import GenericGraphQLError
from apps.core.graphql.mutations import BaseMutationPresenter


class UseCaseMutationOptions(SerializerMutationOptions):
    """Use case mutation options."""

    use_case_class: Optional[Type[BaseUseCase]] = None
    serializer_class: Optional[Type[Serializer]] = None
    presenter_class: Optional[Type[BaseMutationPresenter]] = None


class BaseUseCaseMutation(BaseSerializerMutation):
    """Base class for mutations based on use cases."""

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(  # noqa: WPS211
        cls,
        use_case_class=None,
        presenter_class=None,
        _meta=None,
        **options,
    ):
        """Initialize class with meta."""
        if not _meta:
            _meta = UseCaseMutationOptions(cls)  # noqa: WPS122

        _meta.use_case_class = use_case_class
        _meta.presenter_class = presenter_class
        super().__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> Union["BaseUseCaseMutation", GraphQLError]:
        """Overrideable mutation operation."""
        presenter = cls._meta.presenter_class(cls)
        use_case = cls._meta.use_case_class(presenter)

        try:
            use_case.execute(cls.get_input_dto(root, info, validated_data))
        except BaseApplicationError as err:
            return GenericGraphQLError(err)
        else:
            return presenter.get_response()

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ):
        """Stub for getting usecase input dto."""
