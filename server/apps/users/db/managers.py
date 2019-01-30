from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, login, password=None, **kwargs):
        if not login:
            raise ValueError(_('VN__USER_MUST_HAVE_A_LOGIN'))

        user = self.model(login=login, **kwargs)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password):
        user = self.create_user(
            login,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
