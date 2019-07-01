from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins

from apps.core.rest.views import BaseGenericViewSet
from apps.development.models import Team
from apps.development.rest.filters import TeamMemberFilterBackend
from apps.development.rest.serializers import TeamCardSerializer, TeamSerializer


class TeamsViewset(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   BaseGenericViewSet):
    actions_serializers = {
        'list': TeamCardSerializer,
        'retrieve': TeamSerializer,
    }
    queryset = Team.objects.all()
    search_fields = ('title',)
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
        TeamMemberFilterBackend
    )
    ordering_fields = ('title',)
