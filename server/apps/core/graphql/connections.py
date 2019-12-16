# -*- coding: utf-8 -*-

from graphene import Connection, Int
from graphql import ResolveInfo


class DataSourceConnection(Connection):
    """Datasource connection."""

    count = Int()

    def resolve_count(self, info: ResolveInfo):  # noqa: WPS110
        """Resolve collection length."""
        return self.length

    class Meta:
        """Meta."""

        abstract = True
