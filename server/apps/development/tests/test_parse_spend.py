from datetime import timedelta

from django.test import TestCase

from apps.development.utils.parsers import parse_spend

PARSE_MAP = [
    ('1d 1m', timedelta(days=1, minutes=1)),
    (' 1d  1m  5s', timedelta(days=1, minutes=1, seconds=5)),
    ('1m', timedelta(minutes=1)),
    ('1d 30m', timedelta(days=1, minutes=30)),
    ('1d 30m 15s', timedelta(days=1, minutes=30, seconds=15)),
    ('2w 2d 4h', timedelta(weeks=2, days=2, hours=4)),
    ('0', timedelta(seconds=0)),
    ('', timedelta(seconds=0)),
    (None, timedelta(seconds=0)),
]


class ParseSpendTests(TestCase):
    def test_parse(self):
        for src, dest in PARSE_MAP:
            target_seconds = dest.total_seconds()
            self.assertEqual(parse_spend(src), target_seconds, f'{src} = {target_seconds} secs')
