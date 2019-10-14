from bitfield import BitField as ModelBitField
from bitfield.types import BitHandler

from apps.core.graphql.fields import convert_field_to_float
from apps.core.graphql.fields.bit_field import BitField
from apps.development.models.team_member import TEAM_MEMBER_ROLES


def test_bit_field_serialize():
    keys = TEAM_MEMBER_ROLES.keys()

    bit = BitHandler(1, keys)

    assert BitField().serialize(bit) == ['leader']

    bit = BitHandler(2, keys)

    assert BitField().serialize(bit) == ['developer']

    bit = BitHandler(3, keys)

    assert BitField().serialize(bit) == ['leader', 'developer']


def test_convert_field_to_float():
    roles = ModelBitField(flags=TEAM_MEMBER_ROLES, default=0)

    assert convert_field_to_float(roles).type is not None
