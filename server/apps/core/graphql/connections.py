# -*- coding: utf-8 -*-

from graphene import Connection, Int


class DataSourceConnection(Connection):
    count = Int()

    def resolve_count(self, info):
        return self.length

    class Meta:
        abstract = True
