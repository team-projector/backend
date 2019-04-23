import os
import shutil
import tempfile

import factory
from django.test import TestCase

from fuzzy_checker import FuzzyChecker

TEMP_DIR = os.path.join(tempfile.tempdir, 'test-po')


class FuzzyCheckerTests(TestCase):

    def setUp(self):
        super().setUp()

        self.clean_dir()

    def test_clear_translates(self):
        checker = FuzzyChecker()
        checker.path = TEMP_DIR

        self.create_translates()

        self.assertFalse(checker.run())
        self.clean_dir()

    def test_fuzzy_translates(self):
        checker = FuzzyChecker()
        checker.path = TEMP_DIR

        self.create_translates(True)

        self.assertTrue(checker.run())
        self.clean_dir()

    def create_translates(self, add_errors: bool = False) -> None:
        words = '#, fuzzy' if add_errors else None
        fake_text = self.get_fake_text(words)

        if not os.path.isdir(TEMP_DIR):
            os.makedirs(TEMP_DIR)

        tempfile.tempdir = TEMP_DIR
        tmp_file = tempfile.mktemp(suffix='.po')

        with open(tmp_file, 'wb') as f:
            f.write(str.encode(fake_text))

    @staticmethod
    def clean_dir() -> None:
        if os.path.isdir(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)

    @staticmethod
    def get_fake_text(words: str = '') -> str:
        return f'{factory.Faker("text").generate({})}\n{words}'
