from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token as BaseToken


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


class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('VN__LOGIN'),
                             help_text=_('HT__LOGIN'), unique=True)
    is_staff = models.BooleanField(default=True, verbose_name=_('VN__IS_STAFF'),
                                   help_text=_('HT__IS_STAFF'))
    is_active = models.BooleanField(default=True, verbose_name=_('VN__IS_ACTIVE'), help_text=_('HT__IS_ACTIVE'))

    gl_avatar = models.URLField(null=True, blank=True, verbose_name=_('VN__GITLAB_AVATAR'),
                                help_text=_('HT__GITLAB_AVATAR'), unique=True)

    gl_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('VN__GITLAB_ID'),
                                        help_text=_('HT__GITLAB_ID'))
    gl_url = models.URLField(null=True, blank=True, verbose_name=_('VN__GITLAB_URL'), help_text=_('HT__GITLAB_URL'))
    gl_last_sync = models.DateTimeField(null=True, blank=True, verbose_name=_('VN__GITLAB_LAST_SYNC'),
                                        help_text=_('HT__GITLAB_LAST_SYNC'))

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
