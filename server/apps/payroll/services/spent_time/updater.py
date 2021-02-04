from collections import defaultdict
from typing import DefaultDict, Iterable, List, Union

from django.contrib.contenttypes.models import ContentType

from apps.core.gitlab import parse_gl_date
from apps.development.models import Issue, MergeRequest
from apps.development.models.note import Note, NoteType
from apps.payroll.models import SpentTime  # noqa: WPS433

TIME_SPENTS_NOTES = (NoteType.TIME_SPEND, NoteType.RESET_SPEND)


def adjust_spent_times(work_item: Union[Issue, MergeRequest]) -> None:
    """Create spent times from parsed notes."""
    users_spents: DefaultDict[int, int] = defaultdict(int)

    for note in _get_notes_for_processing(work_item):
        time_spent = 0
        note_date = note.created_at.date()

        if note.type == NoteType.RESET_SPEND:
            time_spent = -users_spents[note.user_id]
            users_spents[note.user_id] = 0
        elif note.type == NoteType.TIME_SPEND:
            time_spent = note.data["spent"]
            note_date = parse_gl_date(note.data["date"])

            users_spents[note.user_id] += note.data["spent"]

        if SpentTime.objects.filter(note=note).exists():
            continue

        SpentTime.objects.create(
            date=note_date,
            created_by=note.user,
            user=note.user,
            time_spent=time_spent,
            note=note,
            base=work_item,
        )


def adjust_spents_times() -> None:
    """Adjust spents times."""
    trackable_content_types = (
        ContentType.objects.get_for_model(Issue),
        ContentType.objects.get_for_model(MergeRequest),
    )

    notes = Note.objects.filter(
        type__in=TIME_SPENTS_NOTES,
        time_spend__isnull=True,
        content_type__in=trackable_content_types,
    )

    for note in notes:
        adjust_spent_times(note.content_object)


def _get_notes_for_processing(
    work_item: Union[Issue, MergeRequest],
) -> Iterable[Note]:
    """
    Get notes for processing.

    :param work_item:
    :type work_item: Union[Issue, MergeRequest]
    :rtype: Iterable[Note]
    """
    notes: List[Note] = []

    for note in work_item.notes.all().order_by("created_at"):
        if note.type == NoteType.MOVED_FROM:
            notes = []
        elif note.type in TIME_SPENTS_NOTES:
            notes.append(note)

    return notes
