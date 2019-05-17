from datetime import timedelta

from django.test import TestCase

from apps.development.services.gitlab.notes import parse_spend

PARSE_MAP = [
    ('1d 1m', timedelta(hours=8, minutes=1)),
    (' 1d  1m  5s', timedelta(hours=8, minutes=1, seconds=5)),
    ('1m', timedelta(minutes=1)),
    ('1d 30m', timedelta(hours=8, minutes=30)),
    ('1d 30m 15s', timedelta(hours=8, minutes=30, seconds=15)),
    ('2w 2d 4h', timedelta(hours=100)),  # 2*5d * 8h + 2*8h + 4h
    ('2mo 2d 4h', timedelta(hours=340)),  # 2*4w*5d*8*h + 2*8h + 4h
    ('0', timedelta(seconds=0)),
    ('', timedelta(seconds=0)),
    (None, timedelta(seconds=0)),
]


class ParseSpendTests(TestCase):
    def test_parse(self):
        for src, dest in PARSE_MAP:
            target_seconds = dest.total_seconds()
            self.assertEqual(parse_spend(src), target_seconds, f'{src} = {target_seconds} secs')
