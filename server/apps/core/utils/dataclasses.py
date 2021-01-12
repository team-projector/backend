import dataclasses
from typing import Dict, List, Optional


def to_dict(
    data_object,
    only_fields: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Converts dataclass to dict."""
    if only_fields is None:
        return dataclasses.asdict(data_object)

    return {
        item_key: item_value
        for item_key, item_value in dataclasses.asdict(data_object).items()
        if item_key in only_fields
    }
