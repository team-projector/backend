# -*- coding: utf-8 -*-

from typing import Dict

from graphql import ResolveInfo
from graphql.utils.ast_to_dict import ast_to_dict


def collect_fields(
    node,
    fragments: Dict[str, object],
):
    """Collect fields."""
    field = {}

    selection_set = node.get('selection_set')

    if selection_set:
        for leaf in selection_set['selections']:
            if leaf['kind'] == 'Field':
                field.update({
                    leaf['name']['value']: collect_fields(leaf, fragments),
                })
            elif leaf['kind'] == 'FragmentSpread':
                field.update(
                    collect_fields(fragments[leaf['name']['value']], fragments),
                )

    return field


def get_fields_from_info(info: ResolveInfo):  # noqa: WPS110
    """Get fields from info."""
    fragments = {}
    node = ast_to_dict(info.field_asts[0])

    for name, fragment_value in info.fragments.items():
        fragments[name] = ast_to_dict(fragment_value)

    return collect_fields(node, fragments)


def is_field_selected(
    info: ResolveInfo,  # noqa: WPS110
    path: str,
) -> bool:
    """Is field selected."""
    fields = get_fields_from_info(info)

    for key in path.split('.'):
        try:
            fields = fields[key]
        except KeyError:
            return False

    return True
