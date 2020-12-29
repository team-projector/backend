from graphene import Connection, Int
from graphql import ResolveInfo


class ModelConnection(Connection):
    """Datasource connection."""

    class Meta:
        """Meta."""

        abstract = True

    count = Int()

    def resolve_count(self, info: ResolveInfo):  # noqa: WPS110
        """Resolve collection length."""
        return self.length
