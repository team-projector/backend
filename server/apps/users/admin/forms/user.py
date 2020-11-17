from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError


class UserAdminForm(UserChangeForm):
    """Show form of User model."""

    def clean_email(self):
        """Check unique email."""
        email = self.cleaned_data.get("email")

        if email:
            emails = self._meta.model.objects.filter(email=email).exclude(
                pk=self.instance.pk,
            )

            if emails.exists():
                raise ValidationError("Value should be unique or empty.")

        return email
