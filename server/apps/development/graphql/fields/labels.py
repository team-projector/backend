from apps.core.graphql.fields import BaseModelConnectionField


class LabelsConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    def __init__(self):
        """Initialize."""
        super().__init__("apps.development.graphql.types.LabelType")
