"""
sending emails
"""

from django.utils import translation
from django.core.mail import send_mail


def translate_for_user(user, *msgs):
    """
    translate msgs for user

    this is typically used when emails are sent to a user
    (who is not the currently active user)

    :param user: User instance
    :param msgs: list of lazy translatable strings
    :return: list of translated strings
    """
    lang = user.profile.language or 'en'
    saved_lang = translation.get_language()
    try:
        translation.activate(lang)
        # "using" the msg triggers lazy translation
        return [msg + u'' for msg in msgs]
    finally:
        translation.activate(saved_lang)


def send_mail_to_user(user, subject, msg, from_addr=None):
    """
    send an email to a specific user

    :param user: User instance
    :param subject: email subject
    :param msg: email plain text
    :param from_addr: sender address (None means DEFAULT_FROM_EMAIL)
    :return:
    """
    return send_mail(subject, msg, from_addr, [user.email], fail_silently=True)
