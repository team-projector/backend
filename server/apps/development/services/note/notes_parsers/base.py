# -*- coding: utf-8 -*-

import re
import types
from collections import defaultdict, namedtuple
from functools import partial
from typing import DefaultDict, Optional, Pattern

from apps.core.utils.time import seconds

RE_SPEND_FULL: Pattern[str] = re.compile(
    r"^(?P<action>(added|subtracted)) (?P<spent>.+) "
    + r"of time spent at (?P<date>\d{4}-\d{2}-\d{2})$",
)
RE_SPEND_SHORT: Pattern[str] = re.compile(
    r"^(?P<action>(added|subtracted)) (?P<spent>.+) of time spent$",
)

RE_SPEND_PART: Pattern[str] = re.compile(
    r"(?P<value>\d+)(?P<part>(mo|w|d|h|m|s))",
)

RE_MOVED_FROM: Pattern[str] = re.compile(r"^moved from .+#\d+$")

RE_ISSUE_NUMBER: Pattern[str] = re.compile(
    r"(^|\s)(#(?P<issue_number>\d+))(\s|[^\w]|$)",
)
RE_GITLAB_ISSUE_LINK: Pattern[str] = re.compile(
    r"(?P<issue_link>https://gitlab.com.*/issues/\d+)",
)


SPEND_RESET_MESSAGE = "removed time spent"

WEEK_PER_MONTH = 4
DAYS_PER_WEEK = 5
HOURS_PER_DAY = 8
HOURS_PER_WEEK = DAYS_PER_WEEK * HOURS_PER_DAY
HOURS_PER_MONTH = WEEK_PER_MONTH * HOURS_PER_WEEK


def spend_handler_helper(
    bag: DefaultDict[str, int], time_value: int, key: str, multiplier: int = 1,
):
    """Helps to handle different units of time via multiplier."""
    bag[key] += time_value * multiplier


hours_helper = partial(spend_handler_helper, key="hours")

GITLAB_SPEND_HANDLERS = types.MappingProxyType(
    {
        "mo": partial(hours_helper, multiplier=HOURS_PER_MONTH),
        "w": partial(hours_helper, multiplier=HOURS_PER_WEEK),
        "d": partial(hours_helper, multiplier=HOURS_PER_DAY),
        "h": hours_helper,
        "m": partial(spend_handler_helper, key="minutes"),
        "s": partial(spend_handler_helper, key="seconds"),
    },
)

NoteReadResult = namedtuple("NoteReadResult", ["type", "data"])


def parse_spend(spent: str) -> int:
    """Parse spent time."""
    # specs https://docs.gitlab.com/ee/workflow/time_tracking.html
    spent = spent or ""
    spent = spent.strip()

    if not spent:
        return 0

    bag: DefaultDict[str, int] = defaultdict(int)

    for part in spent.split(" "):
        match = RE_SPEND_PART.match(part)
        if not match:
            continue

        GITLAB_SPEND_HANDLERS[match.group("part")](
            bag, int(match.group("value")),
        )

    return int(seconds(**bag))


class BaseNoteParser:
    """A base class note parser."""

    def parse(self, gl_note) -> Optional[NoteReadResult]:
        """Method should be implemented."""
        raise NotImplementedError
