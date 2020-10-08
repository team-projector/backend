from django.urls import path

from apps.development.api import views

app_name = "development"

urlpatterns = [
    path("gl-webhook", views.GlWebhookView.as_view(), name="gl-webhook"),
]
