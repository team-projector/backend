from typing import List

from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from jnt_admin_tools.autocomplete_filter import AutocompleteFilter


class ContentTypeFilter(AutocompleteFilter):
    """Content type autocomplete filter."""

    def __init__(  # noqa: WPS211
        self,
        request,
        params,  # noqa: WPS110
        model,
        model_admin,
        models,
    ) -> None:
        """Initialize."""
        self._models = models
        super().__init__(request, params, model, model_admin)
        self._update_url_params()

    def _update_url_params(self) -> None:
        """Update request url."""
        # TODO: need more beauty adding get-params to request.
        url = "/admin/contenttypes/contenttype/autocomplete/"

        self.rendered_widget = format_html(
            self.rendered_widget.replace(  # type: ignore
                url,
                "{0}?ids={1}".format(
                    url,
                    ",".join(
                        (
                            str(content_type.pk)
                            for content_type in self._get_owner_content_types()
                        ),
                    ),
                ),
            ),
        )

    def _get_owner_content_types(self) -> List[ContentType]:
        """Get available content type owner types."""
        return list(
            ContentType.objects.get_for_models(*self._models).values(),
        )
