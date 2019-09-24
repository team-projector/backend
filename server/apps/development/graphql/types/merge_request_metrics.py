# -*- coding: utf-8 -*-

import graphene


class MergeRequestMetricsType(graphene.ObjectType):
    remains = graphene.Int()
    efficiency = graphene.Float()
    payroll = graphene.Float()
    paid = graphene.Float()
