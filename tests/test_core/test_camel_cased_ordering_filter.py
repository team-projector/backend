from apps.core.graphql.filters.ordering import CamelCasedOrderingFilter


def test_camel_case():
    f = CamelCasedOrderingFilter(fields=(
        ('field_i18n', 'field_i18n'),
        'snakes_on_a__plane',
    ))

    assert f.get_ordering_value('fieldI18n') == 'field_i18n'
    assert f.get_ordering_value('snakesOnA__plane') == 'snakes_on_a__plane'


def test_camel_case_input_ad_dict():
    f = CamelCasedOrderingFilter(fields={
        'due_date': 'due_date',
        'user__due_date': 'user__due_date'
    })

    assert f.get_ordering_value('dueDate') == 'due_date'
    assert f.get_ordering_value('user__dueDate') == 'user__due_date'
