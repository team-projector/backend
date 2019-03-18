import re
from typing import List, Pattern

from django.test.runner import DiscoverRunner

RE_EXCLUDE_PATHS: List[Pattern] = [
    re.compile(r'^server.apps\.[a-z_0-9]+\.admin$')
]


class TestRunner(DiscoverRunner):
    def build_suite(self, *args, **kwargs):
        suite = super().build_suite(*args, **kwargs)
        cleanup_tests(suite)
        return suite


def cleanup_tests(suite):
    suite._tests = [t for t in suite._tests if not skip_test(t)]


# HACK
def skip_test(test_case):
    def is_excluded_test_case(test_case) -> bool:
        return any(bool(re_exclude.match(test_case._testMethodName)) for re_exclude in RE_EXCLUDE_PATHS)

    exc = getattr(test_case, '_exception', None)
    return bool(exc and isinstance(exc, ImportError) and is_excluded_test_case(test_case))
