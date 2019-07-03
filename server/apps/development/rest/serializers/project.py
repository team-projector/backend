from rest_framework import serializers

from apps.core.rest.serializers.mixins import TypeSerializerMixin
from apps.development.models import Project


class ProjectCardSerializer(TypeSerializerMixin,
                            serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'gl_id', 'gl_last_sync', 'gl_url', 'title')
