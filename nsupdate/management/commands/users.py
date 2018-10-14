"""
dealing with users (User records in our database)
"""

from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from nsupdate.main.models import Host, Domain

DAY = 24 * 3600  # [s]
T_age = 365 * DAY  # min. age of last login for considering deletion of a user

NEVER = datetime.fromtimestamp(DAY, timezone.utc)  # 2.1.1970

LOG_MSG_DELETE = _("%%(user)r hasn't logged in for %(age)fy, has no hosts and no domains -> deleted user.")
LOG_MSG_HAS_HOSTS = _("%%(user)r kept, has hosts. age: %(age)fy, hosts: %(hosts)d.")
LOG_MSG_HAS_DOMAINS = _("%%(user)r kept, has domains. age: %(age)fy, hosts: %(hosts)d, domains: %(domains)d.")
LOG_MSG_RECENTLY_USED = _("%(user)r kept, was used recently.")


def check_staleness(u):
    """
    checks the staleness of User u (has not logged in for a longer time,
    has no hosts and no domains) and if it is stale, delete it.

    Return log msg (can be None).

    :param u: user instance
    :return: deleted, log_msg
    """
    t_now = timezone.now()
    t_last_login = u.last_login or NEVER
    age = (t_now - t_last_login).total_seconds()
    if age < T_age:
        log_msg = LOG_MSG_RECENTLY_USED
    else:
        age_y = age / 365.0 / DAY
        host_count = Host.objects.filter(created_by=u).count()
        if host_count > 0:
            log_msg = LOG_MSG_HAS_HOSTS % dict(age=age_y, hosts=host_count)
        else:
            domain_count = Domain.objects.filter(created_by=u).count()
            if domain_count > 0:
                log_msg = LOG_MSG_HAS_DOMAINS % dict(age=age_y, hosts=host_count, domains=domain_count)
            else:
                # is not recently used, has no hosts, no domains
                u.delete()
                log_msg = LOG_MSG_DELETE % dict(age=age_y)
    return log_msg


class Command(BaseCommand):
    help = 'deal with users'

    def add_arguments(self, parser):
        parser.add_argument('--stale-check',
                            action='store_true',
                            dest='stale_check',
                            default=False,
                            help='check whether user has logged in recently and has hosts or domains, delete if not')

    def handle(self, *args, **options):
        def print_stats(when):
            user_count = User.objects.all().count()
            host_count = Host.objects.all().count()
            domain_count = Domain.objects.all().count()
            print("%s: users: %d, hosts %d, domains: %d" % (when, user_count, host_count, domain_count))

        stale_check = options['stale_check']
        User = get_user_model()
        with transaction.atomic():
            print_stats("before")
            for u in User.objects.all():
                user = "%s <%s>" % (u.username, u.email)
                log_msg = None
                if stale_check:
                    log_msg = check_staleness(u)
                if log_msg:
                    log_msg = log_msg % dict(user=user)
                    try:
                        self.stdout.write(log_msg)
                    except UnicodeError:
                        pass
            print_stats("after")
