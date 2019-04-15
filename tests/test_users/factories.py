import factory

from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    login = factory.Sequence(lambda n: 'User {0}'.format(n))
    name = factory.Faker('name')
    hour_rate = factory.Faker('random_int', min=0, max=999)
    is_staff = False
    is_active = True

    class Meta:
        model = User
