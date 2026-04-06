"""
Utility functions for sending emails.
"""

from django.utils import translation
from django.core.mail import send_mail


def translate_for_user(user, *msgs):
    """
    Translate messages for a user.

    This is typically used when emails are sent to a user
    (who is not the currently active user).

    :param user: User instance
    :param msgs: List of lazily translatable strings
    :return: List of translated strings
    """
    lang = getattr(user.profile, 'language', None) or 'en'
    saved_lang = translation.get_language()
    try:
        translation.activate(lang)
        # Force evaluation of lazy translation objects by casting to str.
        return [str(msg) for msg in msgs]
    finally:
        translation.activate(saved_lang)


def send_mail_to_user(user, subject, msg, from_addr=None):
    """
    Send an email to a specific user.

    :param user: User instance
    :param subject: Email subject
    :param msg: Email plain text
    :param from_addr: Sender address (None means DEFAULT_FROM_EMAIL)
    :return: Number of successfully delivered messages
    """
    return send_mail(subject, msg, from_addr, [user.email], fail_silently=True)
