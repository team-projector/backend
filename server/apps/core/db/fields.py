from django.db import models


class MoneyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 14
        kwargs['decimal_places'] = 2
        super().__init__(*args, **kwargs)