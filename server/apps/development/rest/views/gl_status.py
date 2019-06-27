from rest_framework import serializers
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.development.rest.serializers import IssueCardSerializer
from apps.development.services.status.gitlab import get_gitlab_sync_status


class GitlabStatusSerializer(serializers.Serializer):
    services = serializers.DictField(child=serializers.DateTimeField())
    last_issues = IssueCardSerializer(many=True)
    last_sync = serializers.DateTimeField()


class GitlabStatusView(BaseGenericAPIView):
    serializer_class = GitlabStatusSerializer

    def get(self, request):
        status = get_gitlab_sync_status()

        return Response(self.get_serializer(status).data)