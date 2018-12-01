from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token as BaseToken


class CustomUserManager(BaseUserManager):
    def create_user(self, login, password=None, **kwargs):
        if not login:
            raise ValueError(_('VN__USERS_MUST_HAVE_AN_LOGIN'))

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


class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('VN__LOGIN'),
                             help_text=_('HT__LOGIN'), unique=True)
    is_staff = models.BooleanField(default=True, verbose_name=_('VN__IS_STAFF'),
                                   help_text=_('HT__IS_STAFF'))
    is_active = models.BooleanField(default=True, verbose_name=_('VN__IS_ACTIVE'), help_text=_('HT__IS_ACTIVE'))
    USERNAME_FIELD = 'login'

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('VN__USER')
        verbose_name_plural = _('VN__USERS')

    def __str__(self):
        return self.login

    def get_short_name(self):
        return self.login


class Token(BaseToken):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('VN__TOKEN')
        verbose_name_plural = _('VN__TOKENS')
