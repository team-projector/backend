from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect
from django.views.generic import TemplateView


class ClearCacheAdminView(TemplateView):
    """Clear cache admin view."""

    title = "Clear cache"
    template_name = "admin/core/clear_cache.html"

    def post(self, request):
        """Main post method."""
        if "clear_cache" in request.POST:
            cache.clear()
            messages.success(request, "Cache cleared successfully!")
        return redirect(request.path)

    def get_context_data(self, **kwargs):
        """Get context data for template."""
        context_data = super().get_context_data(**kwargs)
        context_data.setdefault("title", self.title)

        return context_data
