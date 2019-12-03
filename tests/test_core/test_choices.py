from apps.development.models.note import NOTE_TYPES


def test_equel():
    note_types = (
        ('TIME_SPEND', 'Time spend'),
        ('RESET_SPEND', 'Reset spend'),
        ('MOVED_FROM', 'Moved from'),
    )

    assert NOTE_TYPES == note_types

    note_types = (
        ('TIME_SPEND', 'Time spend'),
        ('RESET_SPEND', 'Reset spend'),
    )

    assert NOTE_TYPES != note_types

    note_types = {
        'TIME_SPEND': 'Time spend',
        'RESET_SPEND': 'Reset spend',
        'MOVED_FROM': 'Moved from',
    }

    assert NOTE_TYPES != note_types


def test_keys():
    assert NOTE_TYPES.keys() == ['TIME_SPEND', 'RESET_SPEND', 'MOVED_FROM']
