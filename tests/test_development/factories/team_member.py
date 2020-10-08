import factory

from apps.development.models import TeamMember


class TeamMemberFactory(factory.django.DjangoModelFactory):
    """Team member factory."""

    class Meta:
        model = TeamMember
