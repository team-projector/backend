# -*- coding: utf-8 -*-

from typing import Optional

from constance import config
from django.contrib.auth.base_user import BaseUserManager
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """The User model manager."""

    @cached_property
    def system_user(self):
        """Get system user."""
        return self.get(login=config.SYSTEM_USER)

    def create_user(
        self, login: str, password: Optional[str] = None, **kwargs,
    ):
        """Create user."""
        if not login:
            raise ValueError(_("VN__USER_MUST_HAVE_A_LOGIN"))

        user = self.model(login=login, **kwargs)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self, login: str, password: str,
    ):
        """Create superuser."""
        user = self.create_user(login, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
