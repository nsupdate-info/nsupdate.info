import re
import base64

import dns.resolver

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models.signals import pre_delete
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now

from . import dnstools


class BlacklistedDomain(models.Model):
    domain = models.CharField(
        max_length=256,
        unique=True,
        help_text='Blacklisted domain. Evaluated as regex (search).')

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.domain, )


def domain_blacklist_validator(value):
    for bd in BlacklistedDomain.objects.all():
        if re.search(bd.domain, value):
            raise ValidationError(u'This domain is not allowed')


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
        max_length=256, unique=True,
        help_text="Name of the zone where dynamic hosts may get added")
    nameserver_ip = models.GenericIPAddressField(
        max_length=256,
        help_text="IP where the dynamic DNS updates for this zone will be sent to")
    nameserver_update_key = models.CharField(
        max_length=256,
        help_text="Shared secret that allows updating this zone (base64 encoded)")
    nameserver_update_algorithm = models.CharField(
        max_length=256, default=UPDATE_ALGORITHM_DEFAULT, choices=UPDATE_ALGORITHM_CHOICES)
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
        max_length=256, default='', blank=True, null=True,
        help_text="Some arbitrary comment about your domain. "
                  "If your domain is public, the comment will be also publicly shown.")

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.domain, )

    def generate_ns_secret(self):
        algorithm = self.nameserver_update_algorithm
        bitlength = UPDATE_ALGORITHMS[algorithm].bitlength
        secret = User.objects.make_random_password(length=bitlength / 8)
        self.nameserver_update_key = key = base64.b64encode(secret)
        self.save()
        return key

    def get_bind9_algorithm(self):
        return UPDATE_ALGORITHMS.get(self.nameserver_update_algorithm).bind_name


class Host(models.Model):
    subdomain = models.CharField(max_length=256, validators=[
        RegexValidator(
            regex=r'^(([a-z0-9][a-z0-9\-]*[a-z0-9])|[a-z0-9])$',
            message='Invalid subdomain: only "a-z", "0-9" and "-" is allowed'
        ),
        domain_blacklist_validator],
        help_text="The name of your host.")
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    update_secret = models.CharField(max_length=256)  # gets hashed on save
    comment = models.CharField(
        max_length=256, default='', blank=True, null=True,
        help_text="Some arbitrary comment about your host, e.g  who / what / where this host is")

    last_update = models.DateTimeField(auto_now=True)
    # when we received the last update for v4/v6 addr
    last_update_ipv4 = models.DateTimeField(blank=True, null=True)
    last_update_ipv6 = models.DateTimeField(blank=True, null=True)
    # how we received the last update for v4/v6 addr
    ssl_update_ipv4 = models.BooleanField()
    ssl_update_ipv6 = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='hosts')

    def __unicode__(self):
        return u"%s.%s - %s" % (
            self.subdomain, self.domain.domain, self.comment)

    class Meta(object):
        unique_together = (('subdomain', 'domain'),)

    def get_fqdn(self):
        return '%s.%s' % (self.subdomain, self.domain.domain)

    @classmethod
    def filter_by_fqdn(cls, fqdn, **kwargs):
        # Assuming subdomain has no dots (.) the fqdn is split at the first dot
        splitted = fqdn.split('.', 1)
        if not len(splitted) == 2:
            raise NotImplemented("FQDN has to contain a dot")
        return Host.objects.filter(
            subdomain=splitted[0], domain__domain=splitted[1], **kwargs)

    def get_ipv4(self):
        try:
            return dnstools.query_ns(self.get_fqdn(), 'A', origin=self.domain.domain)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.Timeout,
                dnstools.NameServerNotAvailable):
            return 'error'

    def get_ipv6(self):
        try:
            return dnstools.query_ns(self.get_fqdn(), 'AAAA', origin=self.domain.domain)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.Timeout,
                dnstools.NameServerNotAvailable):
            return 'error'

    def poke(self, kind, ssl):
        if kind == 'ipv4':
            self.last_update_ipv4 = now()
            self.ssl_update_ipv4 = ssl
        else:
            self.last_update_ipv6 = now()
            self.ssl_update_ipv6 = ssl
        self.save()

    def generate_secret(self, secret=None):
        # note: we use a quick hasher for the update_secret as expensive
        # more modern hashes might put too much load on the servers. also
        # many update clients might use http without ssl, so it is not too
        # secure anyway.
        if secret is None:
            secret = User.objects.make_random_password()
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

pre_delete.connect(pre_delete_host, sender=Host)
