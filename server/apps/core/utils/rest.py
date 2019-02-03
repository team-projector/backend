from rest_framework.request import Request


def parse_query_params(request: Request, serializer_class: type) -> dict:
    serializer = serializer_class(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    return serializer.validated_data
