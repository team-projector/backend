from django.urls import path

from .views import gl_webhook

appname = 'development'

urlpatterns = [
    path('gl-webhook', gl_webhook, name='gl-webhook')
]
