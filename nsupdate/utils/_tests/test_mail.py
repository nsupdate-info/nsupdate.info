"""
Tests for mail module.
"""

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from ..mail import translate_for_user


class TestTransUser(object):
    def test(self):
        User = get_user_model()
        user = User.objects.get(username='test')
        user.profile.language = 'de'
        msgs = [_('German'), _('English')]
        msgs = translate_for_user(user, *msgs)
        assert msgs == ['Deutsch', 'Englisch']
