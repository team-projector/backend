# -*- coding: utf-8 -*-

from typing import List, Optional

from django.db.models import QuerySet
from graphene import Connection, Int, ObjectType, PageInfo
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.settings import graphene_settings
from graphene_django.utils import maybe_queryset
from graphql_relay.connection.arrayconnection import (
    get_offset_with_default,
    offset_to_cursor,
)
from graphql_relay.connection.connectiontypes import Edge

from apps.core.graphql.security.mixins.filter import AuthFilter
from apps.core.graphql.security.permissions import AllowAuthenticated

MAX_SIZE = graphene_settings.RELAY_CONNECTION_MAX_LIMIT


class DataSourceConnectionField(AuthFilter, DjangoFilterConnectionField):
    """Data source connection field."""

    permission_classes = (AllowAuthenticated,)

    def __init__(self, model_type, *args, **kwargs):
        """Initialize self."""
        kwargs.setdefault("offset", Int())
        super().__init__(model_type, *args, **kwargs)

    @classmethod
    def resolve_connection(
        cls, connection, args, iterable,
    ):
        """Resolve connection."""
        iterable = maybe_queryset(iterable)
        if isinstance(iterable, QuerySet):
            items_count = iterable.count()
        else:
            items_count = len(iterable)

        connection = cls._connection_from_list_slice(
            iterable,
            args,
            # differences from original function
            slice_start=args.get("offset", 0),
            list_length=items_count,
            list_slice_length=items_count,
            connection_type=connection,
            edge_type=connection.Edge,
            pageinfo_type=PageInfo,
        )

        connection.iterable = iterable
        connection.length = items_count
        return connection

    @classmethod
    def _connection_from_list_slice(  # noqa: WPS211
        cls,
        list_slice,
        args=None,
        connection_type=Connection,
        edge_type=Edge,
        pageinfo_type=PageInfo,
        slice_start: int = 0,
        list_length: int = 0,
        list_slice_length: Optional[int] = None,
    ) -> Connection:

        # implemented support for offsets

        args = args or {}
        before_offset = get_offset_with_default(
            args.get("before"), list_length,
        )
        after_offset = get_offset_with_default(args.get("after"), -1)

        start_offset = max(slice_start - 1, after_offset, -1) + 1
        end_offset = min(
            slice_start + (list_slice_length or len(list_slice)),
            before_offset,
            list_length,
        )
        if isinstance(args.get("first"), int):
            end_offset = min(end_offset, start_offset + args.get("first"))
        if isinstance(args.get("last"), int):
            start_offset = max(start_offset, end_offset - args.get("last"))

        return cls._build_connection_type(
            connection_type,
            pageinfo_type,
            edge_type,
            list_length,
            list_slice,
            args.get("first"),
            args.get("last"),
            args.get("before"),
            args.get("after"),
            before_offset,
            after_offset,
            start_offset,
            end_offset,
        )

    @classmethod
    def _get_edges(
        cls, edge_type, list_slice, start_offset, end_offset,
    ) -> List[ObjectType]:
        slice_fragment = list_slice[start_offset:end_offset]

        return [
            edge_type(
                node=node, cursor=offset_to_cursor(start_offset + index),
            )
            for index, node in enumerate(slice_fragment)
        ]

    @classmethod
    def _has_previous_page(
        cls, after_offset, after, last, start_offset,
    ) -> bool:
        lower_bound = after_offset + 1 if after else 0

        return isinstance(last, int) and start_offset > lower_bound

    @classmethod
    def _has_next_page(  # noqa: WPS211
        cls, before_offset, before, first, end_offset, list_length,
    ) -> bool:
        upper_bound = before_offset if before else list_length

        return isinstance(first, int) and end_offset < upper_bound

    @classmethod
    def _build_connection_type(  # noqa: WPS211
        cls,
        connection_type,
        pageinfo_type,
        edge_type,
        list_length,
        list_slice,
        first,
        last,
        before,
        after,
        before_offset,
        after_offset,
        start_offset,
        end_offset,
    ) -> Connection:
        # It is differences from original function `connection_from_list_slice`
        if end_offset - start_offset > MAX_SIZE:
            end_offset = start_offset + MAX_SIZE

        edges = cls._get_edges(edge_type, list_slice, start_offset, end_offset)

        return connection_type(
            edges=edges,
            page_info=pageinfo_type(
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
                has_previous_page=cls._has_previous_page(
                    after_offset, after, last, start_offset,
                ),
                has_next_page=cls._has_next_page(
                    before_offset, before, first, end_offset, list_length,
                ),
            ),
        )
