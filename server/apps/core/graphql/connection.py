from graphene import Connection, Int


class DataSourceConnection(Connection):
    total_count = Int()

    def resolve_total_count(self, info):
        return self.length

    class Meta:
        abstract = True
