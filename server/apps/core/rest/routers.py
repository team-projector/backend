from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns


class AppRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        kwargs['trailing_slash'] = False
        super().__init__(*args, **kwargs)


class NoBaseNameRouter(AppRouter):
    """
    This router omits basename part of name param in resulted django url()
    """

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        ret = []

        for _, viewset, _ in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                # Build the url pattern
                regex = route.url.format(
                    prefix='',
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )

                initkwargs = route.initkwargs.copy()
                initkwargs.update({
                    'detail': route.detail,
                })

                name = route.name.replace('{basename}-', '')
                view = viewset.as_view(mapping, **initkwargs)
                ret.append(url(regex, view, name=name))

        ret = format_suffix_patterns(ret)

        return ret

    def get_default_basename(self, *args, **kwargs):
        pass
