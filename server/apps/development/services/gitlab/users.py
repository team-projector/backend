import logging
from typing import Optional

from django.utils import timezone

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from apps.users.models import User

logger = logging.getLogger(__name__)


def extract_user_from_data(data: dict) -> Optional[User]:
    if not data:
        return None

    user_id = data['id']

    user = User.objects.filter(gl_id=user_id).first()
    if not user:
        user = load_user(user_id)

    return user


def update_users() -> None:
    for user in User.objects.filter(gl_id__isnull=False):
        load_user(user.gl_id)


def load_user(user_id: int) -> User:
    gl = get_gitlab_client()

    gl_user = gl.users.get(user_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    user, created = User.objects.update_or_create(
        gl_id=gl_user.id,
        defaults={
            'login': gl_user.username,
            'name': gl_user.name,
            'gl_avatar': gl_user.avatar_url,
            'gl_url': gl_user.web_url,
            'gl_last_sync': timezone.now(),
        })

    if created:
        user.is_active = False
        user.is_staff = False
        user.save()

    if not user.email and gl_user.public_email:
        user.email = gl_user.public_email
        user.save(update_fields=['email'])

    logger.info(f'User "{user}" is synced')

    return user
