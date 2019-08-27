from collections import defaultdict
from typing import DefaultDict

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.development.services.parsers import parse_date


class NotableMixin(models.Model):
    notes = GenericRelation(
        'development.Note',
        verbose_name=_('VN__NOTES'),
        help_text=_('HT__NOTES')
    )

    class Meta:
        abstract = True

    def adjust_spent_times(self) -> None:
        from apps.payroll.models import SpentTime
        from apps.development.models import Note

        users_spents: DefaultDict[int, int] = defaultdict(int)

        for note in self.notes.all().order_by('created_at'):
            time_spent = 0
            note_date = note.created_at.date()

            if note.type == Note.TYPE.reset_spend:
                time_spent = -users_spents[note.user_id]
                users_spents[note.user_id] = 0
            elif note.type == Note.TYPE.time_spend:
                time_spent = note.data['spent']
                note_date = parse_date(note.data['date'])

                users_spents[note.user_id] += note.data['spent']

            if SpentTime.objects.filter(note=note).exists():
                continue

            SpentTime.objects.create(
                date=note_date,
                created_by=note.user,
                user=note.user,
                time_spent=time_spent,
                note=note,
                base=self
            )