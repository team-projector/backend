import typing

import graphql.language
from graphql import GraphQLScalarType, extend_schema, GraphQLSchema


def register_scalar_types(schema: GraphQLSchema,
                          types: typing.List[GraphQLScalarType]):
    for scalar_type in types:
        schema.type_map[scalar_type.name] = scalar_type

    # using a name that already exists in the schema is an error
    # so need to make something up
    dummy_scalar_name = "_extension_dummy"
    extended_schema = extend_schema(
        schema, graphql.language.parse("scalar %s" % dummy_scalar_name)
    )
    # this scalar we extended schema with is not used though
    del extended_schema.type_map[dummy_scalar_name]
    return extended_schema
