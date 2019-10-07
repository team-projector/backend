from apps.development.models.note import NOTE_TYPES


def test_equel():
    note_types = (
        ('time_spend', 'Time spend'),
        ('reset_spend', 'Reset spend'),
        ('moved_from', 'Moved from'),
    )

    assert NOTE_TYPES == note_types

    note_types = (
        ('time_spend', 'Time spend'),
        ('reset_spend', 'Reset spend'),
    )

    assert NOTE_TYPES != note_types

    note_types = {
        'time_spend': 'Time spend',
        'reset_spend': 'Reset spend',
        'moved_from': 'Moved from',
    }

    assert NOTE_TYPES != note_types


def test_keys():
    assert NOTE_TYPES.keys() == ['time_spend', 'reset_spend', 'moved_from']
