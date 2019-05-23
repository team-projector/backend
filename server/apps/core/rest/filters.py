from rest_framework import serializers


class FilterParamUrlSerializer(serializers.Serializer):
    url = serializers.URLField()
