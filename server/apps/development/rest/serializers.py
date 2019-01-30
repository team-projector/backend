from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import IntegerField, Sum
from django.db.models.functions import Cast
from rest_framework import serializers

from apps.core.rest.serializers import LinkSerializer
from apps.users.models import User
from ..models import Issue, Label


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'title', 'color')


class IssueCardSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    time_spent = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'labels', 'project', 'due_date', 'state', 'time_estimate', 'total_time_spent', 'time_spent'
        )

    def get_time_spent(self, instance):
        return instance.notes.filter(user=self.context['request'].user) \
            .annotate(spent=Cast(KeyTextTransform('spent', 'data'), IntegerField())) \
            .aggregate(total_spent=Sum('spent'))['total_spent']


class MetricsParamsSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    start = serializers.DateField()
    end = serializers.DateField()
    group = serializers.CharField()


class MetricSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()
    time_spent = serializers.IntegerField()
    time_estimate = serializers.IntegerField()
    efficiency = serializers.FloatField()
    earnings = serializers.IntegerField()
