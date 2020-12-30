import graphene

from apps.core.graphql.nodes import ModelRelayNode
from apps.payroll.graphql.fields import AllSalariesConnectionField
from apps.payroll.graphql.types import SalaryType


class SalariesQueries(graphene.ObjectType):
    """Class represents list of available fields for salary queries."""

    salary = ModelRelayNode.Field(SalaryType)
    all_salaries = AllSalariesConnectionField()
