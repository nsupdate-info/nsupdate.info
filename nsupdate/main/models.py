"""
models for hosts, domains, service updaters, ...
"""

import re
import base64

import dns.resolver

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models.signals import pre_delete
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now

from . import dnstools


class BlacklistedDomain(models.Model):
    domain = models.CharField(
        max_length=255,
        unique=True,
        help_text='Blacklisted domain. Evaluated as regex (search).')

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blacklisted_domains')

    def __unicode__(self):
        return u"%s" % (self.domain, )


def domain_blacklist_validator(value):
    for bd in BlacklistedDomain.objects.all():
        if re.search(bd.domain, value):
            raise ValidationError(u'This name is blacklisted')


from collections import namedtuple
UpdateAlgorithm = namedtuple("update_algorithm", "bitlength bind_name")

UPDATE_ALGORITHM_DEFAULT = 'HMAC_SHA512'
UPDATE_ALGORITHMS = {
    # dnspython_name -> UpdateAlgorithm namedtuple
    'HMAC_SHA512': UpdateAlgorithm(512, 'hmac-sha512', ),
    'HMAC_SHA384': UpdateAlgorithm(384, 'hmac-sha384', ),
    'HMAC_SHA256': UpdateAlgorithm(256, 'hmac-sha256', ),
    'HMAC_SHA224': UpdateAlgorithm(224, 'hmac-sha224', ),
    'HMAC_SHA1': UpdateAlgorithm(160, 'hmac-sha1', ),
    'HMAC_MD5': UpdateAlgorithm(128, 'hmac-md5', ),
}

UPDATE_ALGORITHM_CHOICES = [(k, k) for k in UPDATE_ALGORITHMS]


class Domain(models.Model):
    domain = models.CharField(
        max_length=255,  # RFC 2181 (and also: max length of unique fields)
        unique=True,
        help_text="Name of the zone where dynamic hosts may get added")
    nameserver_ip = models.GenericIPAddressField(
        max_length=40,  # ipv6 = 8 * 4 digits + 7 colons
        help_text="IP where the dynamic DNS updates for this zone will be sent to")
    nameserver_update_secret = models.CharField(
        max_length=88,  # 512 bits base64 -> 88 bytes
        default='',
        help_text="Shared secret that allows updating this zone (base64 encoded)")
    nameserver_update_algorithm = models.CharField(
        max_length=16,  # see elements of UPDATE_ALGORITHM_CHOICES
        default=UPDATE_ALGORITHM_DEFAULT, choices=UPDATE_ALGORITHM_CHOICES,
        help_text="HMAC_SHA512 is fine for bind9 (you can change this later, if needed)")
    public = models.BooleanField(
        default=False,
        help_text="Check to allow any user to add dynamic hosts to this zone - "
                  "if not checked, we'll only allow the owner to add hosts")
    # available means "nameserver for domain operating and reachable" -
    # gets set to False if we have trouble reaching the nameserver
    available = models.BooleanField(
        default=True,
        help_text="Check if nameserver is available/reachable - "
                  "if not checked, we'll pause querying/updating this nameserver for a while")
    comment = models.CharField(
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text="Some arbitrary comment about your domain. "
                  "If your domain is public, the comment will be also publicly shown.")

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='domains')

    def __unicode__(self):
        return u"%s" % (self.domain, )

    def generate_ns_secret(self):
        algorithm = self.nameserver_update_algorithm
        bitlength = UPDATE_ALGORITHMS[algorithm].bitlength
        user_model = get_user_model()
        secret = user_model.objects.make_random_password(length=bitlength / 8)
        self.nameserver_update_secret = secret_base64 = base64.b64encode(secret)
        self.save()
        return secret_base64

    def get_bind9_algorithm(self):
        return UPDATE_ALGORITHMS.get(self.nameserver_update_algorithm).bind_name


class Host(models.Model):
    subdomain = models.CharField(
        max_length=255,  # RFC 2181 (and considering having multiple joined labels here later)
        validators=[
            RegexValidator(
                regex=r'^(([a-z0-9][a-z0-9\-]*[a-z0-9])|[a-z0-9])$',
                message='Invalid subdomain: only "a-z", "0-9" and "-" is allowed'
            ),
            domain_blacklist_validator,
        ],
        help_text="The name of your host.")
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    update_secret = models.CharField(
        max_length=64,  # secret gets hashed (on save) to salted sha1, 58 bytes str len
    )
    comment = models.CharField(
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text="Some arbitrary comment about your host, e.g  who / what / where this host is")

    # available means that this host may be updated (or not, if False) -
    # gets set to False if abuse happens (client malfunctioning) or
    # if updating this host triggers other errors:
    available = models.BooleanField(
        default=True,
        help_text="Check if host is available/in use - "
                  "if not checked, we won't accept updates for this host")

    # abuse means that we (either the operator or some automatic mechanism)
    # think the host is used in some abusive or unfair way, e.g.:
    # sending nochg updates way too often or otherwise using a defect,
    # misconfigured or otherwise malfunctioning update client
    # acting against fair use / ToS.
    # the abuse flag can be switched off by the user, if the user thinks
    # he fixed the problem on his side (or that there was no problem).
    abuse = models.BooleanField(
        default=False,
        help_text="Checked if we think you abuse the service - "
                  "you may uncheck this AFTER fixing all issues on your side")

    # similar to above, but can not be toggled by the user:
    abuse_blocked = models.BooleanField(
        default=False,
        help_text="Checked to block a host for abuse.")

    # count client misbehaviours, like sending nochg updates or other
    # errors that should make the client stop trying to update:
    client_faults = models.PositiveIntegerField(default=0)

    # count server faults that happened when updating this host
    server_faults = models.PositiveIntegerField(default=0)

    # when we received the last update for v4/v6 addr
    last_update_ipv4 = models.DateTimeField(blank=True, null=True)
    last_update_ipv6 = models.DateTimeField(blank=True, null=True)
    # how we received the last update for v4/v6 addr
    ssl_update_ipv4 = models.BooleanField(default=False)
    ssl_update_ipv6 = models.BooleanField(default=False)

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='hosts')

    def __unicode__(self):
        return u"%s.%s" % (
            self.subdomain, self.domain.domain)

    class Meta(object):
        unique_together = (('subdomain', 'domain'),)

    def get_fqdn(self):
        return '%s.%s' % (self.subdomain, self.domain.domain)

    @classmethod
    def filter_by_fqdn(cls, fqdn, **kwargs):
        # Assuming subdomain has no dots (.) the fqdn is split at the first dot
        splitted = fqdn.split('.', 1)
        if not len(splitted) == 2:
            raise ValueError("FQDN has to contain (at least) one dot")
        hosts = Host.objects.filter(
            subdomain=splitted[0], domain__domain=splitted[1], **kwargs)
        count = len(hosts)
        if count == 0:
            return None
        if count == 1:
            return hosts[0]
        if count > 1:
            raise ValueError("filter_by_fqdn(%s) found more than 1 host" % fqdn)

    def get_ip(self, kind):
        record = 'A' if kind == 'ipv4' else 'AAAA'
        try:
            return dnstools.query_ns(self.get_fqdn(), record, origin=self.domain.domain)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.Timeout,
                dnstools.NameServerNotAvailable):
            return 'error'

    def get_ipv4(self):
        return self.get_ip('ipv4')

    def get_ipv6(self):
        return self.get_ip('ipv6')

    def poke(self, kind, ssl):
        if kind == 'ipv4':
            self.last_update_ipv4 = now()
            self.ssl_update_ipv4 = ssl
        else:
            self.last_update_ipv6 = now()
            self.ssl_update_ipv6 = ssl
        self.save()

    def register_client_fault(self, increment=1):
        self.client_faults += increment
        self.save()

    def register_server_fault(self, increment=1):
        self.server_faults += increment
        self.save()

    def generate_secret(self, secret=None):
        # note: we use a quick hasher for the update_secret as expensive
        # more modern hashes might put too much load on the servers. also
        # many update clients might use http without ssl, so it is not too
        # secure anyway.
        if secret is None:
            user_model = get_user_model()
            secret = user_model.objects.make_random_password()
        self.update_secret = make_password(
            secret,
            hasher='sha1'
        )
        self.save()
        return secret


def pre_delete_host(sender, **kwargs):
    obj = kwargs['instance']
    try:
        dnstools.delete(obj.get_fqdn(), origin=obj.domain.domain)
    except (dnstools.Timeout, dnstools.NameServerNotAvailable):
        # well, we tried to clean up, but we didn't reach the nameserver
        pass
    except (dnstools.DnsUpdateError, ):
        # e.g. PeerBadSignature if host is protected by a key we do not have
        pass

pre_delete.connect(pre_delete_host, sender=Host)


class ServiceUpdater(models.Model):
    name = models.CharField(
        max_length=32,
        help_text="Service name")
    comment = models.CharField(
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text="Some arbitrary comment about the service")
    server = models.CharField(
        max_length=255,  # should be enough
        help_text="Update Server [name or IP] of this service")
    path = models.CharField(
        max_length=255,  # should be enough
        default='/nic/update',
        help_text="Update Server URL path of this service")
    secure = models.BooleanField(
        default=True,
        help_text="Use https / SSL to contact the Update Server?")

    # what kind(s) of IPs is (are) acceptable to this service:
    accept_ipv4 = models.BooleanField(default=False)
    accept_ipv6 = models.BooleanField(default=False)

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='serviceupdater')

    def __unicode__(self):
        return u"%s" % (self.name, )


class ServiceUpdaterHostConfig(models.Model):
    service = models.ForeignKey(ServiceUpdater, on_delete=models.CASCADE)

    hostname = models.CharField(
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text="The hostname for that service (used in query string)")
    comment = models.CharField(
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text="Some arbitrary comment about your host on that service")
    # credentials for http basic auth for THAT service (not for us),
    # we need to store the password in plain text, we can't hash it
    name = models.CharField(
        max_length=255,  # should be enough
        help_text="The name/id for that service (used for http basic auth)")
    password = models.CharField(
        max_length=255,  # should be enough
        help_text="The password/secret for that service (used for http basic auth)")

    # what kind(s) of IPs should be given to this service:
    give_ipv4 = models.BooleanField(default=False)
    give_ipv6 = models.BooleanField(default=False)

    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='serviceupdaterhostconfigs')

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='serviceupdaterhostconfigs')

    def __unicode__(self):
        return u"%s (%s)" % (self.hostname, self.service.name, )
