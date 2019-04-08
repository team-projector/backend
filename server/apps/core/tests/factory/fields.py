from functools import partial

import factory


class UniqueField(factory.Sequence):
    def __init__(self, provider, **kwargs):
        super().__init__(partial(self.wrapper, provider, kwargs), int)

    @staticmethod
    def wrapper(provider, kwargs, step):
        return f'{factory.Faker(provider, **kwargs).generate({})}{step}'
