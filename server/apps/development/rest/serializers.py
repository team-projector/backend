from rest_framework import serializers

from apps.core.rest.serializers import LinkSerializer
from ..models import Issue, Label


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'title', 'color')


class IssueCardSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    dueDate = serializers.DateField(source='due_date')
    timeEstimate = serializers.IntegerField(source='time_estimate')

    class Meta:
        model = Issue
        fields = ('id', 'title', 'labels', 'project', 'dueDate', 'state', 'timeEstimate')
