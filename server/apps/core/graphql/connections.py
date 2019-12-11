# -*- coding: utf-8 -*-

from graphene import Connection, Int
from graphql import ResolveInfo


class DataSourceConnection(Connection):
    count = Int()

    def resolve_count(
        self,
        info: ResolveInfo,  # noqa: WPS110
    ):
        return self.length

    class Meta:
        abstract = True
