import re
from datetime import datetime

import dns.resolver

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models.signals import post_delete
from django.contrib.auth.hashers import make_password

from main import dnstools


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


class Domain(models.Model):
    domain = models.CharField(max_length=256, unique=True)
    nameserver_ip = models.IPAddressField(
        max_length=256,
        help_text="An IP where the nsupdates for this domain will be sent to")
    nameserver_update_key = models.CharField(max_length=256)

    last_update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.domain, )


class Host(models.Model):
    subdomain = models.CharField(max_length=256, validators=[
        RegexValidator(
            regex=r'^(([a-z0-9][a-z0-9\-]*[a-z0-9])|[a-z0-9])$',
            message='Invalid subdomain: only "a-z", "0-9" and "-" is allowed'
        ),
        domain_blacklist_validator])
    domain = models.ForeignKey(Domain)
    update_secret = models.CharField(max_length=256)  # gets hashed on save
    comment = models.CharField(
        max_length=256, default='', blank=True, null=True)

    last_update = models.DateTimeField(auto_now=True)
    last_api_update = models.DateTimeField(blank=True, null=True)
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

    def getIPv4(self):
        try:
            return dnstools.query_ns(self.get_fqdn(), 'A')
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return ''

    def getIPv6(self):
        try:
            return dnstools.query_ns(self.get_fqdn(), 'AAAA')
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return ''

    def poke(self):
        self.last_api_update = datetime.now()
        self.save()

    def generate_secret(self):
        # note: we use a quick hasher for the update_secret as expensive
        # more modern hashes might put too much load on the servers. also
        # many update clients might use http without ssl, so it is not too
        # secure anyway.
        secret = User.objects.make_random_password()
        self.update_secret = make_password(
            secret,
            hasher='sha1'
        )
        self.save()
        return secret


def post_delete_host(sender, **kwargs):
    obj = kwargs['instance']
    dnstools.delete(obj.get_fqdn())

post_delete.connect(post_delete_host, sender=Host)
