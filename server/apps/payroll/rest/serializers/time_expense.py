from rest_framework import serializers
from rest_framework.fields import Field

from apps.payroll.models import SpentTime


class OwnerSerializerField(Field):
    def to_representation(self, instance):
        serializer = self.get_field_serializer(instance)

        if serializer:
            return serializer(
                instance,
                context=self.context
            ).data

    def get_field_serializer(self, instance):
        from apps.development.models import Issue, MergeRequest
        from apps.development.rest.serializers import (
            IssueCardSerializer, MergeRequestCardSerializer
        )

        serializers_map = {
            Issue: IssueCardSerializer,
            MergeRequest: MergeRequestCardSerializer
        }

        return serializers_map.get(instance._meta.model)


class TimeExpenseSerializer(serializers.ModelSerializer):
    owner = OwnerSerializerField(source='base')

    class Meta:
        model = SpentTime
        fields = (
            'id', 'created_at', 'updated_at', 'date', 'time_spent', 'owner')
