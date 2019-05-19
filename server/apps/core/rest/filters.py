from django.conf import settings
from rest_framework import serializers


class FilterParamUrlSerializer(serializers.Serializer):
    url = serializers.URLField()

    def validate_url(self, value):
        if settings.GITLAB_HOST not in value:
            raise serializers.ValidationError("invalid url param")

        return value
