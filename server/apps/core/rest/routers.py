from rest_framework.routers import DefaultRouter


class AppRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        kwargs['trailing_slash'] = False
        super().__init__(*args, **kwargs)
