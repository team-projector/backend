from rest_framework import serializers


class FilterParamUrlSerializer(serializers.Serializer):
    url = serializers.URLField()

    def validate_url(self, value):
        # TODO: validate conditions
        if 'gitlab.com' not in value:
            raise serializers.ValidationError("invalid url param")

        return value
