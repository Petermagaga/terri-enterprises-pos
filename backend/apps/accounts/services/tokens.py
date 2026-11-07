from rest_framework.authtoken.models import Token


def get_user_token(user):
    """
    Return the existing authentication token or create one.
    Each user has one persistent token.
    """
    token, _ = Token.objects.get_or_create(user=user)
    return token


def revoke_user_token(user):
    """
    Delete the user's authentication token.
    This logs the user out.
    """
    Token.objects.filter(user=user).delete()