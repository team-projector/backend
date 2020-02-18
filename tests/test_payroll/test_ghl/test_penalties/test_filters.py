from apps.payroll.graphql.filters import PenaltyFilterSet
from apps.payroll.models import Penalty
from tests.test_payroll.factories import PenaltyFactory
from tests.test_users.factories.user import UserFactory


def test_salaries_filter_by_user(user):
    PenaltyFactory.create_batch(size=3, user=user)

    user_2 = UserFactory.create()
    salaries_user_2 = PenaltyFactory.create_batch(size=5, user=user_2)

    results = PenaltyFilterSet(
        data={"user": user_2.id},
        queryset=Penalty.objects.all(),
    ).qs

    assert results.count() == 5
    assert set(results) == set(salaries_user_2)
