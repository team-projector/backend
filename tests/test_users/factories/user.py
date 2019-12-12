import factory

from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    login = factory.Sequence(lambda n: f'User {n}')
    name = factory.Sequence(lambda n: f'User name {n}')
    hour_rate = factory.Faker('random_int', min=0, max=999)
    is_staff = False
    is_active = True

    class Meta:
        model = User
