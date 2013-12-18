"""
dealing with the fault counters and available/abuse/abuse_blocked flags
"""

from optparse import make_option

from django.core.management.base import BaseCommand

from nsupdate.main.models import Host


class Command(BaseCommand):
    help = 'deal with the faults counters'

    option_list = BaseCommand.option_list + (
        make_option('--show-server',
                    action='store_true',
                    dest='show_server',
                    default=False,
                    help='show server fault counters',
        ),
        make_option('--show-client',
                    action='store_true',
                    dest='show_client',
                    default=False,
                    help='show client fault counters',
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
                    help='reset the client fault counters of all hosts',
        ),
        make_option('--reset-abuse',
                    action='store_true',
                    dest='reset_abuse',
                    default=False,
                    help='reset the abuse flag (to False) of all hosts',
        ),
        make_option('--reset-abuse-blocked',
                    action='store_true',
                    dest='reset_abuse_blocked',
                    default=False,
                    help='reset the abuse_blocked flag (to False) of all hosts',
        ),
        make_option('--reset-available',
                    action='store_true',
                    dest='reset_available',
                    default=True,
                    help='reset the available flag (to True) of all hosts',
        ),
        make_option('--flag-abuse',
                    action='store',
                    dest='flag_abuse',
                    default=None,
                    type='int',
                    help='if client faults > N then set abuse flag and reset client faults',
        ),
    )

    def handle(self, *args, **options):
        show_client = options['show_client']
        show_server = options['show_server']
        reset_client = options['reset_client']
        reset_server = options['reset_server']
        reset_available = options['reset_available']
        reset_abuse = options['reset_abuse']
        reset_abuse_blocked = options['reset_abuse_blocked']
        flag_abuse = options['flag_abuse']
        for h in Host.objects.all():
            if show_client or show_server:
                output = u""
                if show_client:
                    output += u"%-6d " % h.client_faults
                if show_server:
                    output += u"%-6d " % h.server_faults
                output += u"%s %s\n" % (h.created_by.username, h.get_fqdn(), )
                self.stdout.write(output)
            if (flag_abuse is not None or reset_client or reset_server or
                reset_available or reset_abuse or reset_abuse_blocked):
                if flag_abuse is not None:
                    if h.client_faults > flag_abuse:
                        h.abuse = True
                        self.stdout.write("setting abuse flag for host %s (created by %s, client faults: %d)\n" % (
                                          h.get_fqdn(), h.created_by, h.client_faults))
                        h.client_faults = 0
                if reset_client:
                    h.client_faults = 0
                if reset_server:
                    h.server_faults = 0
                if reset_available:
                    h.available = True
                if reset_abuse:
                    h.abuse = False
                if reset_abuse_blocked:
                    h.abuse_blocked = False
                h.save()
