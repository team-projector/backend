"""URLs module"""
from django.conf import settings
from django.urls import path
from social_core.utils import setting_name
from social_django import views

from . import social_views

extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''

app_name = 'social'

urlpatterns = [
    # authentication / association
    path('login/<slug:backend>/', views.auth, name='begin'),
    path('complete/<slug:backend>/', social_views.complete, name='complete'),
    # disconnection
    path('disconnect/<slug:backend>/', views.disconnect, name='disconnect'),
    path('disconnect/<slug:backend>/<int:association_id>/', views.disconnect, name='disconnect_individual'),
]
