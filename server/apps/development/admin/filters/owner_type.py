from typing import List

from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from jnt_admin_tools.autocomplete_filter import AutocompleteFilter

from apps.development.models import Project, ProjectGroup

OWNER_TYPES = (Project, ProjectGroup)


def _get_owner_content_types() -> List[ContentType]:
    """Get available content type owner types."""
    return list(ContentType.objects.get_for_models(*OWNER_TYPES).values())


class OwnerContentTypeFilter(AutocompleteFilter):
    """Autocomplete filter by type of owner."""

    title = "owner type"
    field_name = "content_type"

    def __init__(self, *args, **kwargs) -> None:
        """Initializing."""
        super().__init__(*args, **kwargs)
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
                            for content_type in _get_owner_content_types()
                        ),
                    ),
                ),
            ),
        )
