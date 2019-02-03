from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token as BaseToken

from apps.users.db.managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('VN__LOGIN'),
                             help_text=_('HT__LOGIN'), unique=True)
    name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('VN__NAME'),
                            help_text=_('HT__NAME'), unique=True)
    email = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('VN__LOGIN'),
                             help_text=_('HT__LOGIN'), unique=True)
    hour_rate = models.DecimalField(default=0, decimal_places=2, max_digits=10,
                                    verbose_name=_('VN__HOUR_RATE'), help_text=_('HT__HOUR_RATE'))
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
        ordering = ('login',)

    def __str__(self):
        return self.login

    def get_short_name(self):
        return self.login


class Token(BaseToken):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('VN__TOKEN')
        verbose_name_plural = _('VN__TOKENS')
