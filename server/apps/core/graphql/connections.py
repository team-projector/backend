# -*- coding: utf-8 -*-

from graphene import Connection, Int


class DataSourceConnection(Connection):
    """Data source connection."""

    count = Int()

    def resolve_count(self, info):  # noqa: WPS110
        """Get count."""
        return self.length

    class Meta:
        abstract = True
