import factory
import pytz

from apps.development.models import Note
from tests.test_development.factories import MergeRequestFactory


class MergeRequestNoteFactory(factory.django.DjangoModelFactory):
    """Merge request note factory."""

    class Meta:
        model = Note

    gl_id = factory.Sequence(lambda seq: seq)
    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=pytz.UTC,
    )
    content_object = factory.SubFactory(MergeRequestFactory)
    data = {}  # noqa: WPS110
