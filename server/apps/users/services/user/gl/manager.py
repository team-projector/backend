# -*- coding: utf-8 -*-

import logging
from typing import Optional

from django.utils import timezone

from apps.users.models import User
from apps.users.services.user.gl.provider import UserGlProvider

logger = logging.getLogger(__name__)


class UserGlManager:
    """Users gitlab manager."""

    def __init__(self):
        """Initializing."""
        self.user_provider = UserGlProvider()

    def sync_users(self) -> None:
        """Load users from Gitlab."""
        for user in User.objects.filter(gl_id__isnull=False):
            self.sync_user(user.gl_id)

    def sync_user(
        self,
        gl_user_id: int,
    ) -> User:
        """Load user from Gitlab."""
        gl_user = self.user_provider.get_gl_user(gl_user_id)

        user, created = User.objects.update_or_create(
            gl_id=gl_user.id,
            defaults={
                "login": gl_user.username,
                "name": gl_user.name,
                "gl_avatar": gl_user.avatar_url,
                "gl_url": gl_user.web_url,
                "gl_last_sync": timezone.now(),
            })

        if created:
            user.is_active = False
            user.is_staff = False
            user.save()

        if not user.email and gl_user.public_email:
            user.email = gl_user.public_email
            user.save(update_fields=("email",))

        logger.info("User '%s' is synced", user)

        return user

    def extract_user_from_data(
        self,
        gl_user,
    ) -> Optional[User]:
        """Retrieve Gitlab user."""
        if not gl_user:
            return None

        user = User.objects.filter(gl_id=gl_user["id"]).first()
        if not user:
            user = self.sync_user(gl_user["id"])

        return user
