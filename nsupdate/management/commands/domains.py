"""
dealing with domains (Domain records in our database)
"""

import dns.resolver
import dns.message

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from nsupdate.main.models import Domain, Host
from nsupdate.main.dnstools import FQDN, query_ns, NameServerNotAvailable
from nsupdate.utils.mail import translate_for_user, send_mail_to_user

MSG = _("""\
Your domain: %(domain)s (comment: %(comment)s)

Issue: The nameserver of the domain is not reachable and was set to not available
       (and also to not public, in case it was public).

Explanation:
You created the domain on our service and entered a primary nameserver IP for it.
We tried to query that nameserver but it either was not reachable or it did not
answer queries for this domain.

Resolution:
If you really want that domain to work and you really control that nameserver:

1. fix the nameserver so it responds to queries for this domain
2. make sure the nameserver is reachable from us
3. make sure it accepts dynamic updates for hosts in this domain
4. make sure it uses the same secret as configured on the service
5. set the domain to "available" on the service
6. check if the "public" flag is correctly

Alternatively, if you do not use the domain with our service, delete the
domain entry, so it is removed from our database. This will also remove all
hosts that were added to this domain (if any).
""")


LOG_MSG_IS_AVAILABLE = _('Domain %(domain)s is available.')
LOG_MSG_HAS_HOSTS = _('Domain %%(domain)s is not available, but has %(hosts)d hosts.')
LOG_MSG_DELETE = _('Domain %(domain)s is not available and has no hosts -> deleted domain.')


def check_dns(domain):
    """
    checks if the nameserver is reachable and answers queries for the domain.

    note: we can't reasonably check for dynamic updates as the dns admin might
    have put restrictions on which hosts are allowed to be updated.

    :param domain: domain name
    :return: available status
    """
    fqdn = FQDN(host=None, domain=domain)
    try:
        query_ns(fqdn, 'SOA', prefer_primary=True)
        queries_ok = True
    except (dns.resolver.Timeout, dns.resolver.NoNameservers,
            dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, NameServerNotAvailable, dns.message.UnknownTSIGKey):
        # note: currently the domain is also set to unavailable as a
        # side effect in query_ns()
        queries_ok = False
    return queries_ok


def check_staleness(d):
    """
    checks the staleness of Domain d (is not available and has no hosts) and if it is stale, delete it.

    Return log msg (can be None).

    :param d: Domain instance
    :return: log_msg
    """
    if d.available:
        log_msg = LOG_MSG_IS_AVAILABLE
    else:
        host_count = Host.objects.filter(domain=d).count()
        if host_count > 0:
            log_msg = LOG_MSG_HAS_HOSTS % dict(hosts=host_count)
        else:
            # is not available and has no hosts
            d.delete()
            log_msg = LOG_MSG_DELETE
    return log_msg


class Command(BaseCommand):
    help = 'deal with domains'

    def add_arguments(self, parser):
        parser.add_argument('--check',
                            action='store_true',
                            dest='check',
                            default=False,
                            help='check whether nameserver for domain is reachable and answers queries')
        parser.add_argument('--notify-user',
                            action='store_true',
                            dest='notify_user',
                            default=False,
                            help='notify the user by email when domain gets flagged as unavailable')
        parser.add_argument('--stale-check',
                            action='store_true',
                            dest='stale_check',
                            default=False,
                            help='check whether domain is available or has hosts, delete if not')

    def handle(self, *args, **options):
        check = options['check']
        stale_check = options['stale_check']
        notify_user = options['notify_user']
        with transaction.atomic():
            for d in Domain.objects.all():
                domain = d.name
                if check and d.available:
                    comment = d.comment
                    creator = d.created_by
                    available = check_dns(domain)
                    if not available:
                        d.available = False  # see comment in check_dns()
                        d.public = False
                        if notify_user:
                            subject, msg = translate_for_user(
                                creator,
                                _("issue with your domain %(domain)s"),
                                MSG
                            )
                            subject = subject % dict(domain=domain)
                            msg = msg % dict(domain=domain, comment=comment)
                            send_mail_to_user(creator, subject, msg)
                        msg = "setting unavailable flag for domain %s (created by %s)\n" % (domain, creator,)
                        self.stdout.write(msg)
                    d.save()
                if stale_check:
                    log_msg = check_staleness(d)
                    if log_msg:
                        log_msg = log_msg % dict(domain=domain)
                        self.stdout.write(log_msg)
