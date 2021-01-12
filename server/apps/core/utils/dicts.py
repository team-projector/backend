def set_value_if_none(data_dict, item_key: str, item_value: object) -> None:
    """Set value if dict value is null."""
    try:
        data_value = data_dict[item_key]
    except KeyError:
        return
    else:
        if data_value is None:
            data_dict[item_key] = item_value
