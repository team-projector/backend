from .can_view_user_metrics import CanViewUserMetrics


class CanViewEmbeddedUserMetrics(CanViewUserMetrics):
    def has_object_permission(self, request, view, user):
        show_metrics = request.query_params.get('metrics', 'false') != 'false'
        if not show_metrics:
            return True

        return super().has_object_permission(request, view, user)
