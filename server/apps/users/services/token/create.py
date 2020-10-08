from apps.users.models import Token, User


def create_user_token(user: User) -> Token:
    """Create token for user."""
    return Token.objects.create(user=user)
