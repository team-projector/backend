from graphene.test import Client

from django.utils import timezone

from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import SalaryFactory
from server.gql import schema


def data():
    return {
        'charged_time': 3,
        'payed': True,
        'bonus': 10.15,
        'period_to': timezone.now().date() + timezone.timedelta(days=1),
        'taxes': 1.65,
        'penalty': 2.75,
        'period_from': timezone.now().date() - timezone.timedelta(days=1),
        'sum': 50.15,
        'total': 10.25
    }


def test_retrieve(user):
    client = Client(schema)

    TeamMemberFactory.create(team=TeamFactory.create(), user=user)
    salary = SalaryFactory.create(user=user, **data())

    result = client.execute(
        f'''{{
          salary (id: {salary.id}) {{
            id
            createdAt
            periodFrom
            periodTo
            chargedTime
            bonus
            taxes
            penalty
            sum
            total
            payed
          }}
        }}
        ''',
        context=salary
    )

    assert result['data']['salary']['id'] == str(salary.id)
    assert result['data']['salary']['createdAt'] is not None
    assert result['data']['salary']['periodFrom'] == str(data()['period_from'])
    assert result['data']['salary']['periodTo'] == str(data()['period_to'])
    assert result['data']['salary']['chargedTime'] == data()['charged_time']
    assert result['data']['salary']['bonus'] == data()['bonus']
    assert result['data']['salary']['taxes'] == data()['taxes']
    assert result['data']['salary']['penalty'] == data()['penalty']
    assert result['data']['salary']['sum'] == data()['sum']
    assert result['data']['salary']['total'] == data()['total']
    assert result['data']['salary']['payed'] == data()['payed']
