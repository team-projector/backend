# from graphql.execution.utils import collect_fields
from django.db.models import QuerySet
from graphql.utils.ast_to_dict import ast_to_dict

from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.types import IssueType
from apps.development.models import Issue


def collect_fields(node,
                   fragments) -> dict:
    """Recursively collects fields from the AST
    Args:
        node (dict): A node in the AST
        fragments (dict): Fragment definitions
    Returns:
        A dict mapping each field found, along with their sub fields.
        {'name': {},
         'sentimentsPerLanguage': {'id': {},
                                   'name': {},
                                   'totalSentiments': {}},
         'slug': {}}
    """

    field = {}

    if node.get('selection_set'):
        for leaf in node['selection_set']['selections']:
            if leaf['kind'] == 'Field':
                field.update({
                    leaf['name']['value']: collect_fields(leaf, fragments)
                })
            elif leaf['kind'] == 'FragmentSpread':
                field.update(collect_fields(fragments[leaf['name']['value']],
                                            fragments))

    return field


def get_fields(info) -> dict:
    """A convenience function to call collect_fields with info
    Args:
        info (ResolveInfo)
    Returns:
        dict: Returned from collect_fields
    """

    fragments = {}
    node = ast_to_dict(info.field_asts[0])

    for name, value in info.fragments.items():
        fragments[name] = ast_to_dict(value)

    return collect_fields(node, fragments)


class IssueNode(IssueType):
    class Meta:
        model = Issue
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection

    @classmethod
    def get_queryset(cls,
                     queryset,
                     info) -> QuerySet:
        if cls.is_field_selected(info, 'edges.node.user'):
            queryset = queryset.select_related('user')

        if cls.is_field_selected(info, 'edges.node.participants'):
            queryset = queryset.prefetch_related('participants')

        return queryset

    @classmethod
    def is_field_selected(cls,
                          info,
                          path: str) -> bool:
        fields = get_fields(info)

        for key in path.split('.'):
            try:
                fields = fields[key]
            except KeyError:
                return False

        return True
