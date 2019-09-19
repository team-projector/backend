from apps.development.models import Label
from tests.base import model_admin
from tests.test_development.factories import LabelFactory


def test_color_square(db):
    ma_label = model_admin(Label)

    label = LabelFactory.create(color='#74b800')

    assert '#74b800' in ma_label.color_square(label)
