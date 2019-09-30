# -*- coding: utf-8 -*-

from graphql.utils.ast_to_dict import ast_to_dict


def collect_fields(
    node,
    fragments,
) -> dict:
    field = {}

    if node.get('selection_set'):
        for leaf in node['selection_set']['selections']:
            if leaf['kind'] == 'Field':
                field.update({
                    leaf['name']['value']: collect_fields(leaf, fragments),
                })
            elif leaf['kind'] == 'FragmentSpread':
                field.update(
                    collect_fields(fragments[leaf['name']['value']], fragments),
                )

    return field


def get_fields_from_info(info) -> dict:
    fragments = {}
    node = ast_to_dict(info.field_asts[0])

    for name, value in info.fragments.items():
        fragments[name] = ast_to_dict(value)

    return collect_fields(node, fragments)


def is_field_selected(
    info,
    path: str,
) -> bool:
    fields = get_fields_from_info(info)

    for key in path.split('.'):
        try:
            fields = fields[key]
        except KeyError:
            return False

    return True
