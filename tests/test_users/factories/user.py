import factory

from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    class Meta:
        model = User

    login = factory.Sequence(lambda seq: "User {0}".format(seq))
    name = factory.Sequence(lambda seq: "User name {0}".format(seq))
    hour_rate = factory.Faker("random_int", min=100, max=999)
    is_staff = False
    is_active = True
    roles = User.roles.MANAGER
