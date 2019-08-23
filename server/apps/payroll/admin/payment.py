from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.users.admin.filters import UserFilter
from ..models import Payment


@admin.register(Payment)
class PaymentAdmin(BaseModelAdmin):
    list_display = ('user', 'created_by', 'created_at', 'sum')
    list_filter = (UserFilter,)
    search_fields = ('user__login', 'user__email')
