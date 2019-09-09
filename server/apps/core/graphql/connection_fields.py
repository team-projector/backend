from django.db.models import QuerySet
from graphene import Connection, Int, PageInfo
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.settings import graphene_settings
from graphene_django.utils import maybe_queryset
from graphql_relay.connection.arrayconnection import (
    get_offset_with_default,
    offset_to_cursor
)
from graphql_relay.connection.connectiontypes import Edge

from apps.core.graphql.security.mixins.filter import AuthFilter
from apps.core.graphql.security.permissions import AllowAuthenticated


class DataSourceConnectionField(AuthFilter,
                                DjangoFilterConnectionField):
    permission_classes = (AllowAuthenticated,)

    def __init__(self, model_type, *args, **kwargs):
        kwargs.setdefault('offset', Int())
        super().__init__(model_type, *args, **kwargs)

    @classmethod
    def resolve_connection(cls,
                           connection,
                           default_manager,
                           args,
                           iterable):
        if iterable is None:
            iterable = default_manager

        iterable = maybe_queryset(iterable)
        if isinstance(iterable, QuerySet):
            if iterable is not default_manager:
                default_queryset = maybe_queryset(default_manager)
                iterable = cls.merge_querysets(default_queryset, iterable)
            items_count = iterable.count()
        else:
            items_count = len(iterable)

        connection = cls._connection_from_list_slice(
            iterable,
            args,
            # differences from original function
            slice_start=args.get('offset', 0),
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
    def _connection_from_list_slice(cls, list_slice,
                                    args=None,
                                    connection_type=None,
                                    edge_type=None,
                                    pageinfo_type=None,
                                    slice_start=0,
                                    list_length=0,
                                    list_slice_length=None):

        # implemented support for offsets

        connection_type = connection_type or Connection
        edge_type = edge_type or Edge
        pageinfo_type = pageinfo_type or PageInfo

        args = args or {}

        before = args.get('before')
        after = args.get('after')
        first = args.get('first')
        last = args.get('last')
        if list_slice_length is None:
            list_slice_length = len(list_slice)
        slice_end = slice_start + list_slice_length
        before_offset = get_offset_with_default(before, list_length)
        after_offset = get_offset_with_default(after, -1)

        start_offset = max(
            slice_start - 1,
            after_offset,
            -1
        ) + 1
        end_offset = min(
            slice_end,
            before_offset,
            list_length
        )
        if isinstance(first, int):
            end_offset = min(
                end_offset,
                start_offset + first
            )
        if isinstance(last, int):
            start_offset = max(
                start_offset,
                end_offset - last
            )

        # It is differences from original function `connection_from_list_slice`
        max_size = graphene_settings.RELAY_CONNECTION_MAX_LIMIT
        if end_offset - start_offset > max_size:
            end_offset = start_offset + max_size

        slice_fragment = list_slice[start_offset:end_offset]
        edges = [
            edge_type(
                node=node,
                cursor=offset_to_cursor(start_offset + i)
            )
            for i, node in enumerate(slice_fragment)
        ]

        first_edge_cursor = edges[0].cursor if edges else None
        last_edge_cursor = edges[-1].cursor if edges else None
        lower_bound = after_offset + 1 if after else 0
        upper_bound = before_offset if before else list_length

        return connection_type(
            edges=edges,
            page_info=pageinfo_type(
                start_cursor=first_edge_cursor,
                end_cursor=last_edge_cursor,
                has_previous_page=(
                    isinstance(last, int) and start_offset > lower_bound),
                has_next_page=(
                    isinstance(first, int) and end_offset < upper_bound
                )
            )
        )
