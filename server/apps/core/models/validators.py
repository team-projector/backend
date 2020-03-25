# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def tax_rate_validator(tax_rate: float) -> None:
    """Tax rate validator."""
    if 0 <= tax_rate <= 1:
        return

    raise ValidationError(_("MSG__VALUE_MUST_BE_FROM_0_TO_1"))
