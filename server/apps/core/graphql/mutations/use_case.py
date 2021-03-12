from typing import Dict, Optional, Type, Union

from graphql import GraphQLError, ResolveInfo
from jnt_django_graphene_toolbox.errors import (
    GraphQLInputError,
    GraphQLPermissionDenied,
)
from jnt_django_graphene_toolbox.mutations import BaseMutation
from jnt_django_graphene_toolbox.mutations.serializer import (
    SerializerMutationOptions,
)

from apps.core.application.errors import (
    AccessDeniedApplicationError,
    BaseApplicationError,
    InvalidInputApplicationError,
)
from apps.core.application.use_cases import BaseUseCase
from apps.core.graphql.errors import GenericGraphQLError


class UseCaseMutationOptions(SerializerMutationOptions):
    """Use case mutation options."""

    use_case_class: Optional[Type[BaseUseCase]] = None


class BaseUseCaseMutation(BaseMutation):
    """Base class for mutations based on use cases."""

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(  # noqa: WPS211
        cls,
        use_case_class=None,
        _meta=None,
        **options,
    ):
        """Initialize class with meta."""
        if not _meta:
            _meta = UseCaseMutationOptions(cls)  # noqa: WPS122

        _meta.use_case_class = use_case_class
        super().__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> Union["BaseUseCaseMutation", GraphQLError]:
        """Overrideable mutation operation."""
        use_case = cls._meta.use_case_class()

        try:
            output_dto = use_case.execute(
                cls.get_input_dto(root, info, **kwargs),
            )
        except InvalidInputApplicationError as err:
            return GraphQLInputError(err.errors)
        except AccessDeniedApplicationError:
            return GraphQLPermissionDenied()
        except BaseApplicationError as err:
            return GenericGraphQLError(err)

        return cls(
            **cls.get_response_data(root, info, output_dto),
        )

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ):
        """Stub for getting usecase input dto."""

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto,
    ) -> Dict[str, object]:
        """Stub for getting usecase input dto."""
