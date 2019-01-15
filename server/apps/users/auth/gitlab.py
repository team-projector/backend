from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from apps.users.models import User


class GitLabAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = User.objects.filter(gl_id=sociallogin.account.uid).first()

        if not user:
            raise ValueError('User not found')

        sociallogin.user = user
        return super().save_user(request, sociallogin, form)
