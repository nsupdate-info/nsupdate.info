import uuid
from django.core.cache import cache


def generate_detectip_token(session_key):
    """
    Generate a short-lived random token for a session key and store it in the cache.
    :param session_key: The Django session key
    :return: A random hex string
    """
    token = uuid.uuid4().hex
    # Use a short timeout of 60 seconds, which is enough to load the detectip image
    cache.set('detectip_token:%s' % token, session_key, timeout=60)
    return token


def get_session_key_from_token(token):
    """
    Retrieve a session key from the cache using a token.
    :param token: The token string
    :return: The session key string or None
    """
    return cache.get('detectip_token:%s' % token)
