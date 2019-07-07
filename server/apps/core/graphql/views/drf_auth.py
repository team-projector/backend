from graphene_django.views import GraphQLView
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.settings import api_settings


class DrfAuthenticatedGraphQLView(GraphQLView):
    def parse_body(self, request):
        if isinstance(request, Request):
            return request.data

        return super().parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        view = permission_classes((IsAuthenticated,))(view)
        view = authentication_classes(
            api_settings.DEFAULT_AUTHENTICATION_CLASSES
        )(view)
        view = api_view(['GET', 'POST'])(view)
        return view
