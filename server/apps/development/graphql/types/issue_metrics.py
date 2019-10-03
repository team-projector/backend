# -*- coding: utf-8 -*-

import graphene


class IssueMetricsType(graphene.ObjectType):
    """
    A class representing issues metrics fields.
    """
    remains = graphene.Int()
    efficiency = graphene.Float()
    payroll = graphene.Float()
    paid = graphene.Float()
