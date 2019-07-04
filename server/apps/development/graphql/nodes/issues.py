import graphene
from django.db.models import Sum
from graphene import Connection, Int, ObjectType, relay
from graphene_django import DjangoObjectType

from apps.development.models import Issue
from apps.payroll.models import SpentTime
from apps.users.models import User


class TotalCountMixin(ObjectType):
    @classmethod
    def get_connection(cls):
        class CountableConnection(relay.Connection):
            total_count = Int()

            class Meta:
                name = '{}Connection'.format(cls._meta.name)
                node = cls

            @staticmethod
            def resolve_total_count(root, args, context, info):
                return root.length

        return CountableConnection


class DataSourceConnection(Connection):
    total_count = Int()

    def resolve_total_count(self, info):
        return self.length

    class Meta:
        abstract = True


class IssueMetrics(graphene.ObjectType):
    remains = graphene.Int()
    efficiency = graphene.Float()
    payroll = graphene.Float()
    paid = graphene.Float()


class IssueNode(DjangoObjectType):
    id = graphene.ID(source='pk')
    metrics = graphene.Field(IssueMetrics)

    def resolve_metrics(self, info, **kwargs):
        instance: Issue = self

        payroll = SpentTime.objects.filter(
            issues__id=instance.id
        ).aggregate_payrolls()

        return {
            'remains': instance.time_remains,
            'efficiency': instance.efficiency,
            'payroll': payroll['total_payroll'],
            'paid': payroll['total_paid'],
        }

    class Meta:
        model = Issue
        filter_fields = ['title']
        interfaces = (relay.Node,)
        connection_class = DataSourceConnection


class UserType(DjangoObjectType):
    class Meta:
        model = User
