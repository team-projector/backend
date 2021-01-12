from jnt_django_graphene_toolbox.fields import BaseModelConnectionField


class LabelsConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__("apps.development.graphql.types.LabelType")
