from django.forms.models import model_to_dict


def model_to_dict_form(object_data: dict) -> dict:
    """
    Model to dict form.

    :param object_data:
    :type object_data: dict
    :rtype: dict
    """
    original = model_to_dict(object_data)
    return {
        field_key: "" if field_value is None else field_value
        for field_key, field_value in original.items()
    }
