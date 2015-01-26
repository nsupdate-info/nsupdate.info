"""
dealing with domains (Domain records in our database)
"""

import dns.resolver

from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from nsupdate.main.models import Domain
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
            dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, NameServerNotAvailable):
        # note: currently the domain is also set to unavailable as a
        # side effect in query_ns()
        queries_ok = False
    return queries_ok


class Command(BaseCommand):
    help = 'deal with domains'

    option_list = BaseCommand.option_list + (
        make_option('--check',
                    action='store_true',
                    dest='check',
                    default=False,
                    help='check whether nameserver for domain is reachable and answers queries',
        ),
        make_option('--notify-user',
                    action='store_true',
                    dest='notify_user',
                    default=False,
                    help='notify the user by email when domain gets flagged as unavailable',
        ),
    )

    def handle(self, *args, **options):
        check = options['check']
        notify_user = options['notify_user']
        with transaction.atomic():
            for d in Domain.objects.all():
                if check and d.available:
                    domain = d.name
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
                        msg = "setting unavailable flag for domain %s (created by %s)\n" % (domain, creator, )
                        self.stdout.write(msg)
                    d.save()
