"""
models for account-related stuff
"""

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import text_type


@python_2_unicode_compatible
class UserProfile(models.Model):
    """
    stuff we need additionally to what Django stores in User model
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name='profile',
                                verbose_name=_('user'), on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES,
                                default='', blank=True, null=True,
                                verbose_name=_('language'))

    def __str__(self):
        return u"profile for %s" % text_type(self.user)

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')


def create_user_profile(sender, instance=None, created=False, **kwargs):
    # if a new user is created, create the UserProfile also:
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)


@receiver(user_logged_in)
def lang(sender, user=None, request=None, **kwargs):
    # if a user logs in, activate language preference from profile
    request.session[LANGUAGE_SESSION_KEY] = user.profile.language
