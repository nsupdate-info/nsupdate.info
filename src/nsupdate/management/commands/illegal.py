"""
try to identify users / hosts doing illegal / questionable things
"""

import time
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import OperationalError

from nsupdate.main.models import Host
from nsupdate.main import dnstools


class Command(BaseCommand):
    help = 'try to identify users / hosts doing illegal / questionable things'

    def handle(self, *args, **options):
        ip_to_hosts = defaultdict(list)
        for host in Host.objects.all():
            fqdn = host.get_fqdn()
            try:
                ip = dnstools.query_ns(fqdn, 'A')
                ip_to_hosts[ip].append(host)
            except:
                pass
        ips = sorted(ip_to_hosts.keys(), key=lambda ip: len(ip_to_hosts[ip]), reverse=True)
        for ip in ips:
            users = {}
            hosts_of_user = defaultdict(list)
            hosts = ip_to_hosts[ip]
            ip_refcount = len(hosts)
            print("IP %s is referred to by %d hosts." % (ip, ip_refcount))
            for host in hosts:
                user = host.created_by
                users[user.id] = user
                hosts_of_user[user.id].append(host)
            response = None
            for user_id in users:
                user = users[user_id]
                count = len(hosts_of_user[user_id])
                hostname_samples = ', '.join(h.name for h in hosts_of_user[user_id][:10])
                print("User %s (%s) has created %d hosts all pointing to same IP as %d other hostnames." % (user.username, user.email, count, ip_refcount - count))
                print("Hostname samples: %s" % (hostname_samples, ))
                if response != 'Y':
                    response = input("Delete user? no [default], y = yes, Y = YES to all, a = abort > ")
                if response.lower() == 'y':
                    while True:
                        try:
                            user.delete()
                            break
                        except OperationalError:
                            # database is locked
                            time.sleep(0.1)
                if response.lower() == 'a':
                    break
