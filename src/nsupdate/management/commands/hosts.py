"""
Deal with hosts (Host records in our database).
"""

from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nsupdate.main.models import Host
from nsupdate.utils.mail import translate_for_user, send_mail_to_user

DAY = 24 * 3600  # [s]
T_ip = 325 * DAY  # Age of last IP update when we start considering the host as stale.
T_react = 8 * DAY  # Time the owner has to react to a notification before staleness increases and next notification.
S_notstale = 0  # Staleness level meaning the host is NOT stale.
S_unavailable = 3  # Staleness level that makes the host unavailable.
S_delete = 5  # Staleness level that leads to the host being deleted.

NEVER = datetime.fromtimestamp(DAY, timezone.utc)  # 2.1.1970

LOG_MSG_STALE = _("%(host)s has not seen IP updates for a long time; staleness: %(staleness)d -> please fix!")
LOG_MSG_UNAVAILABLE = _("%(host)s IP has still not been updated, staleness: %(staleness)d -> made host unavailable.")
LOG_MSG_DELETE = _("%(host)s IP has still not been updated, staleness: %(staleness)d -> deleted host.")

EMAIL_MSG_START = _("""\
Your host: %(host)s (comment: %(comment)s)

Issue: \
""")

EMAIL_MSG_END = _("""

Explanation:
You created the host on our service, but it has not been updated for a very long time.

That might be because:
* You don't use the host/service anymore, but forgot to delete the host.
* The host IP never changed and thus did not require an update.
* Your update credentials are wrong and thus updates are not working.
* Your updater is malfunctioning and not sending updates.

We can't know the reason. But please understand that we do not want to
accumulate unused hosts in our database, so please help resolve this issue.

We will send some notifications like this to remind you to resolve this.
If you do not react and resolve this, your host will first be made unavailable
and later it will be deleted.

Resolution:
* If you still use the host:
  - If your host was switched to unavailable, you first need to manually set
    it to available again (via the web interface).
  - Send an update for it (you can do that via the web interface or by just
    accessing the update URL or by forcing your update software to send an
    update). An update with the same IP is acceptable in this case.
* If you do not use the host anymore, please delete it from the service.

Hint: To avoid this issue for static or mostly static IP hosts, consider
sending one unconditional update every month. Some DynDNS2-compatible updaters
can do that, too.
""")

EMAIL_MSG_END_DELETED = _("""

Explanation:
You created the host on our service, but it has not been updated for a very long time.

We sent you some email notifications about this, but you never reacted to them.
Thus, we assume that you do not need the host anymore and have DELETED it.

Feel free to re-create it on our service in case you need it again at some
time.
""")


def check_staleness(h):
    """
    Check the staleness of host h and, if it is stale, react by increasing the
    staleness counter. When the counter reaches certain thresholds, first make the host
    unavailable, then remove the host.

    Return email message and log message (each can be None).

    :param h: Host instance
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
            h.staleness = staleness  # IP has been updated recently.
            changed = True
    elif notification_age < T_react:
        pass  # Since we notified, not enough time has passed for the owner to react.
    else:
        staleness = old_staleness + 1
        if staleness >= S_delete:
            h.delete()
            EMAIL_MSG_DELETE = u"%s%s%s" % (EMAIL_MSG_START, LOG_MSG_DELETE, EMAIL_MSG_END_DELETED)
            email_msg, log_msg = EMAIL_MSG_DELETE, LOG_MSG_DELETE
        elif staleness >= S_unavailable:
            h.staleness = staleness
            h.available = False  # TODO: Remove host from DNS also.
            h.staleness_notification_timestamp = t_now
            changed = True
            EMAIL_MSG_UNAVAILABLE = u"%s%s%s" % (EMAIL_MSG_START, LOG_MSG_UNAVAILABLE, EMAIL_MSG_END)
            email_msg, log_msg = EMAIL_MSG_UNAVAILABLE, LOG_MSG_UNAVAILABLE
        else:
            h.staleness = staleness
            h.staleness_notification_timestamp = t_now
            changed = True
            EMAIL_MSG_STALE = u"%s%s%s" % (EMAIL_MSG_START, LOG_MSG_STALE, EMAIL_MSG_END)
            email_msg, log_msg = EMAIL_MSG_STALE, LOG_MSG_STALE
    if changed:
        h.save()
    return staleness, email_msg, log_msg


class Command(BaseCommand):
    help = 'Deal with hosts.'

    def add_arguments(self, parser):
        parser.add_argument('--stale-check',
                            action='store_true',
                            dest='stale_check',
                            default=False,
                            help='Check whether the host has been updated recently; increase staleness counter if not.')
        parser.add_argument('--notify-user',
                            action='store_true',
                            dest='notify_user',
                            default=False,
                            help='Notify the user by email when the staleness counter increases.')

    def handle(self, *args, **options):
        stale_check = options['stale_check']
        notify_user = options['notify_user']
        with transaction.atomic():
            for h in Host.objects.all():
                if stale_check:
                    host = h.name + "." + h.domain.name
                    comment = h.comment
                    creator = h.created_by
                    staleness, email_msg, log_msg = check_staleness(h)
                    if email_msg and notify_user:
                        subject, msg = translate_for_user(
                            creator,
                            _("Issue with your host %(host)s"),
                            email_msg
                        )
                        subject = subject % dict(host=host)
                        email_msg = email_msg % dict(host=host, staleness=staleness, comment=comment)
                        send_mail_to_user(creator, subject, email_msg)
                    if log_msg:
                        log_msg = log_msg % dict(host=host, staleness=staleness, creator=creator)
                        self.stdout.write(log_msg)
