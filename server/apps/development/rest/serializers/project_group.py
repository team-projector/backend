from rest_framework import serializers

from apps.core.rest.mixins.serializers import TypeSerializerMixin
from apps.development.models import ProjectGroup


class ProjectGroupCardSerializer(TypeSerializerMixin,
                                 serializers.ModelSerializer):
    class Meta:
        model = ProjectGroup
        fields = ('id', 'gl_id', 'gl_last_sync', 'gl_url', 'title')
