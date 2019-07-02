from rest_framework import serializers

from apps.core.rest.mixins.serializers import TypeSerializerMixin
from apps.core.rest.serializers import LinkSerializer
from apps.development.models import MergeRequest
from apps.development.rest.serializers import LabelSerializer
from apps.development.rest.serializers.issue import MetricsMixin
from apps.users.rest.serializers import UserCardSerializer


class MergeRequestCardSerializer(TypeSerializerMixin,
                                 MetricsMixin,
                                 serializers.ModelSerializer):
    labels = LabelSerializer(many=True)
    project = LinkSerializer()
    time_spent = serializers.SerializerMethodField()
    milestone = LinkSerializer()
    user = UserCardSerializer(source='author')

    class Meta:
        model = MergeRequest
        fields = (
            'gl_url', 'gl_last_sync', 'gl_id', 'time_spent', 'title', 'labels',
            'total_time_spent', 'project', 'state', 'user', 'milestone',
            'time_estimate', 'id',
        )
