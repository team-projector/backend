from rest_framework import serializers

from apps.development.models import ProjectGroup


class ProjectGroupCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectGroup
        fields = ('id', 'gl_id', 'gl_last_sync', 'gl_url', 'title')
