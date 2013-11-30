"""
reinitialize the test user account (and clean up)
"""

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from nsupdate.main.models import Host


class Command(BaseCommand):
    help = 'deal with the faults counters'

    option_list = BaseCommand.option_list + (
        make_option('--show-server',
            action='store_true',
            dest='show_server',
            default=False,
            help='reset the server fault counters of all hosts',
        ),
        make_option('--show-client',
            action='store_true',
            dest='show_client',
            default=False,
            help='reset the server fault counters of all hosts',
        ),
        make_option('--reset-server',
            action='store_true',
            dest='reset_server',
            default=False,
            help='reset the server fault counters of all hosts',
        ),
        make_option('--reset-client',
            action='store_true',
            dest='reset_client',
            default=False,
            help='reset the client faults counters of all hosts',
        ),
    )
    def handle(self, *args, **options):
        show_client = options['show_client']
        show_server = options['show_server']
        reset_client = options['reset_client']
        reset_server = options['reset_server']
        for h in Host.objects.all():
            if show_client or show_server:
                output = u""
                if show_client:
                    output += u"%-6d " % h.client_faults
                if show_server:
                    output += u"%-6d " % h.server_faults
                output += u"%s %s\n" % (h.created_by.username, h.get_fqdn(), )
                self.stdout.write(output)
            if reset_client or reset_server:
                if reset_client:
                    h.client_faults = 0
                if reset_server:
                    h.server_faults = 0
                h.save()
