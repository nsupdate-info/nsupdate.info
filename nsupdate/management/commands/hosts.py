"""
dealing with hosts (Host records in our database)
"""

from datetime import datetime
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from nsupdate.main.models import Host

DAY = 24 * 3600  # [s]
T_ip = 325 * DAY  # age of last ip update so we starts considering host as stale
T_react = 8 * DAY  # time owner has to react to a notification before staleness increases & next notification
S_notstale = 0  # staleness level telling host is NOT stale
S_unavailable = 3  # staleness level leading to host being made unavailable
S_delete = 5  # staleness level leading to host being deleted

NEVER = datetime.fromtimestamp(DAY, timezone.utc)  # 2.1.1970

LOG_MSG_STALE = "%(host)s has not seen IP updates since a long time, staleness: %(staleness)d -> please fix!"
LOG_MSG_UNAVAILABLE = "%(host)s IP has still not been updated, staleness: %(staleness)d -> made host unavailable."
LOG_MSG_DELETE = "%(host)s IP has still not been updated, staleness: %(staleness)d -> deleted host."

EMAIL_MSG_START = """\
Your host: %(host)s (comment: %(comment)s)

Issue: \
"""

EMAIL_MSG_END = """

Explanation:
You created the host on our service, but it has not been updated for a very long time.

That might be because:
* you don't use the host/service any more, but forgot to delete the host
* host IP never changed and thus did not require an update
* your update credentials are wrong and thus updates are not working
* your updater is malfunctioning and not sending updates

We can't know what the reason is. But please understand that we do not want to
accumulate unused hosts in our database, so please help resolving this issue.

We will send some notifications like this to remind you to resolve this.
If you do not react and resolve this, your host will first be made unavailable
and later it will be deleted.

Resolution:
* if you still use the host:
  - if your host was switched to unavailable, you first need to manually set
    it to available again (via the web interface).
  - send an update for it (you can do that via the web interface or by just
    accessing the update URL or by forcing your update software to send an
    update). An update with same IP is acceptable in this case.
* if you do not use the host any more, please delete it from the service

Hint: to avoid this issue for static or mostly-static IP hosts, consider
sending 1 unconditional update every month. some dyndns2 compatible updaters
can do that, too.
"""

EMAIL_MSG_END_DELETED = """

Explanation:
You created the host on our service, but it has not been updated for a very long time.

We sent you some email notifications about this, but you never reacted to them.
Thus, we assume that you do not need the host any more and have DELETED it.

Feel free to re-create it on our service in case you need it again at some
time.
"""

EMAIL_MSG_STALE = EMAIL_MSG_START + LOG_MSG_STALE + EMAIL_MSG_END
EMAIL_MSG_UNAVAILABLE = EMAIL_MSG_START + LOG_MSG_UNAVAILABLE + EMAIL_MSG_END
EMAIL_MSG_DELETE = EMAIL_MSG_START + LOG_MSG_DELETE + EMAIL_MSG_END_DELETED


def check_staleness(h):
    """
    checks the staleness of Host h and if it stale, react by increasing the
    staleness counter. When counter reaches some threshold, first make host
    unavailable, then remove host.

    Return email msg and log msg (each can be None).

    :param h:
    :return: email_msg, log_msg
    """
    email_msg = log_msg = None
    t_now = timezone.now()
    last_update_ipv4 = h.last_update_ipv4 or NEVER
    last_update_ipv6 = h.last_update_ipv6 or NEVER
    last_update_ip = max(last_update_ipv4, last_update_ipv6)
    ip_age = (t_now - last_update_ip).total_seconds()
    staleness = old_staleness = h.staleness
    last_notification = h.staleness_notification_timestamp or NEVER
    notification_age = (t_now - last_notification).total_seconds()
    changed = False
    if ip_age < T_ip:
        staleness = S_notstale
        if old_staleness != staleness:
            h.staleness = staleness  # ip has been updated recently
            changed = True
    elif notification_age < T_react:
        pass  # since we notified, not enough time has passed for owner to react
    else:
        staleness = old_staleness + 1
        if staleness >= S_delete:
            h.delete()
            email_msg, log_msg = EMAIL_MSG_DELETE, LOG_MSG_DELETE
        elif staleness >= S_unavailable:
            h.staleness = staleness
            h.available = False  # TODO remove host from dns also
            h.staleness_notification_timestamp = t_now
            changed = True
            email_msg, log_msg = EMAIL_MSG_UNAVAILABLE, LOG_MSG_UNAVAILABLE
        else:
            h.staleness = staleness
            h.staleness_notification_timestamp = t_now
            changed = True
            email_msg, log_msg = EMAIL_MSG_STALE, LOG_MSG_STALE
    if changed:
        h.save()
    return staleness, email_msg, log_msg


class Command(BaseCommand):
    help = 'deal with hosts'

    option_list = BaseCommand.option_list + (
        make_option('--stale-check',
                    action='store_true',
                    dest='stale_check',
                    default=False,
                    help='check whether the host has been updated recently, increase staleness counter if not',
        ),
        make_option('--notify-user',
                    action='store_true',
                    dest='notify_user',
                    default=False,
                    help='notify the user by email when staleness counter increases',
        ),
    )

    def handle(self, *args, **options):
        stale_check = options['stale_check']
        notify_user = options['notify_user']
        with transaction.atomic():
            for h in Host.objects.all():
                if stale_check:
                    host = h.name
                    comment = h.comment
                    creator = h.created_by
                    staleness, email_msg, log_msg = check_staleness(h)
                    if email_msg and notify_user:
                        from_addr = None  # will use DEFAULT_FROM_EMAIL
                        to_addr = creator.email
                        subject = "issue with your host %(host)s" % dict(host=host)
                        email_msg = email_msg % dict(host=host, staleness=staleness, comment=comment)
                        send_mail(subject, email_msg, from_addr, [to_addr], fail_silently=True)
                    if log_msg:
                        log_msg = log_msg % dict(host=host, staleness=staleness, creator=creator)
                        self.stdout.write(log_msg)
