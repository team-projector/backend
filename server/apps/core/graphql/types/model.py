from typing import Optional

import graphene
from django.db.models import Model, QuerySet
from graphene import Connection
from graphene.types.objecttype import ObjectTypeOptions
from graphene_django.utils import is_valid_django_model
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.core.graphql.connections import ModelConnection
from apps.core.graphql.nodes import ModelRelayNode


class ModelObjectTypeOptions(ObjectTypeOptions):
    """Options for type."""

    model: Optional[Model] = None
    connection: Optional[graphene.Connection] = None
    auth_required: bool = False


class BaseModelObjectType(graphene.ObjectType):
    """Base class for graphql types."""

    @classmethod
    def __init_subclass_with_meta__(  # noqa: C901 R701 WPS211 WPS210 WPS231
        cls,
        model=None,
        name=None,
        connection_class=None,
        use_connection=None,
        auth_required=False,
        interfaces=(),
        _meta=None,
        **options,
    ):
        """Applying meta information."""
        if not is_valid_django_model(model):
            raise ValueError(
                'You need to pass a valid Django Model in {0}.Meta, received "{1}".'.format(  # noqa: E501
                    cls.__name__,
                    model,
                ),
            )

        if not name:
            name = model.__name__
        if not interfaces:
            interfaces = (ModelRelayNode,)
        if not connection_class:
            connection_class = ModelConnection

        if use_connection is None and interfaces:
            use_connection = any(
                (
                    issubclass(interface, graphene.Node)
                    for interface in interfaces
                ),
            )

        connection = None
        if use_connection:
            # We create the connection automatically
            if not connection_class:
                connection_class = graphene.Connection

            connection = connection_class.create_type(
                "{0}Connection".format(options.get("name") or cls.__name__),
                node=cls,
            )

        if connection is not None and not issubclass(connection, Connection):
            raise ValueError(
                "The connection must be a Connection. Received {0}".format(
                    connection.__name__,
                ),
            )

        if not _meta:
            _meta = ModelObjectTypeOptions(cls)  # noqa: WPS122

        _meta.model = model
        _meta.connection = connection
        _meta.auth_required = auth_required

        super().__init_subclass_with_meta__(
            name=name,
            interfaces=interfaces,
            _meta=_meta,
            **options,
        )

    @classmethod
    def is_type_of(cls, root, info: ResolveInfo):  # noqa: WPS110
        """Check is type of."""
        if isinstance(root, cls):
            return True
        if not is_valid_django_model(root.__class__):
            raise ValueError(
                'Received incompatible instance "{0}".'.format(root),
            )

        if cls._meta.model._meta.proxy:  # noqa: WPS437
            model = root._meta.model  # noqa: WPS437
        else:
            model = root._meta.model._meta.concrete_model  # noqa: WPS437

        return model == cls._meta.model

    @classmethod
    def get_queryset(
        cls,
        queryset: QuerySet,
        info: ResolveInfo,  # noqa: WPS110
    ) -> QuerySet:
        """Provide queryset."""
        return queryset

    @classmethod
    def get_node(cls, info: ResolveInfo, id):  # noqa: WPS110 WPS125
        """Get node by id."""
        if cls._meta.auth_required and not info.context.user.is_authenticated:
            return GraphQLPermissionDenied()

        queryset = cls.get_queryset(cls._meta.model.objects, info)
        try:
            return queryset.get(pk=id)
        except cls._meta.model.DoesNotExist:
            return None

    def resolve_id(self, info: ResolveInfo):  # noqa: WPS110
        """Returns object primary key."""
        return self.pk
