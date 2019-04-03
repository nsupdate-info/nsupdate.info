"""
reinitialize the test user account (and clean up)
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'reinitialize the test user'

    def handle(self, *args, **options):
        user_model = get_user_model()
        try:
            u = user_model.objects.get(username='test')
            # delete test user and (via CASCADE behaviour) everything that
            # points to it (has user as ForeignKey), e.g. via created_by.
            u.delete()
        except user_model.DoesNotExist:
            pass
        # create a fresh test user
        u = user_model.objects.create_user('test', settings.DEFAULT_FROM_EMAIL, 'test')
        u.save()
        self.stdout.write('Successfully reinitialized the test user')
