from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.rest.views import BaseGenericAPIView
from apps.development.models import Issue
from apps.development.rest.filters import IssueStatusUrlFilter


class GitlabIssieStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ('id', 'title', 'state', 'is_merged')


class GitlabIssueStatusView(BaseGenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = GitlabIssieStatusSerializer
    queryset = Issue.objects.all()
    filter_backends = (IssueStatusUrlFilter,)

    def get(self, request, format=None):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(self.get_serializer(
            queryset.first()
        ).data)
