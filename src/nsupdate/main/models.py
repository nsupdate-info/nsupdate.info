"""
models for hosts, domains, service updaters, ...
"""

import re
import time
import base64

import dns.resolver
import dns.message

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models.signals import pre_delete, post_save
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import text_type

from . import dnstools

RESULT_MSG_LEN = 255


def result_fmt(msg):
    """
    format the message for storage into client/server_result_msg fields
    """
    msg = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time())) + ' ' + msg
    return msg[:RESULT_MSG_LEN]


@python_2_unicode_compatible
class BlacklistedHost(models.Model):
    name_re = models.CharField(
        _('name RegEx'),
        max_length=255,
        unique=True,
        help_text=_('Blacklisted domain. Evaluated as regex (search).'))

    last_update = models.DateTimeField(_('last update'), auto_now=True)
    created = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='blacklisted_domains',
        verbose_name=_('created by'), on_delete=models.CASCADE)

    def __str__(self):
        return self.name_re

    class Meta:
        verbose_name = _('blacklisted host')
        verbose_name_plural = _('blacklisted hosts')


def host_blacklist_validator(value):
    for bd in BlacklistedHost.objects.all():
        if re.search(bd.name_re, value):
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


@python_2_unicode_compatible
class Domain(models.Model):
    name = models.CharField(
        _("name"),
        max_length=255,  # RFC 2181 (and also: max length of unique fields)
        validators=[RegexValidator(regex=r"([a-zA-Z0-9-_]+\.)+[a-zA-Z0-9-_]{2,}", message=_("Invalid domain name"))],
        unique=True,
        help_text=_("Name of the zone where dynamic hosts may get added"))
    nameserver_ip = models.GenericIPAddressField(
        _("nameserver IP (primary)"),
        max_length=40,  # ipv6 = 8 * 4 digits + 7 colons
        help_text=_("IP where the dynamic DNS updates for this zone will be sent to"))
    nameserver2_ip = models.GenericIPAddressField(
        _("nameserver IP (secondary)"),
        max_length=40,  # ipv6 = 8 * 4 digits + 7 colons
        blank=True, null=True,
        help_text=_("IP where DNS queries for this zone will be sent to"))
    nameserver_update_secret = models.CharField(
        _("nameserver update secret"),
        max_length=88,  # 512 bits base64 -> 88 bytes
        default='',
        help_text=_("Shared secret that allows updating this zone (base64 encoded)"))
    nameserver_update_algorithm = models.CharField(
        _("nameserver update algorithm"),
        max_length=16,  # see elements of UPDATE_ALGORITHM_CHOICES
        default=UPDATE_ALGORITHM_DEFAULT, choices=UPDATE_ALGORITHM_CHOICES,
        help_text=_("HMAC_SHA512 is fine for bind9 (you can change this later, if needed)"))
    public = models.BooleanField(
        _("public"),
        default=False,
        help_text=_("Check to allow any user to add dynamic hosts to this zone - "
                    "if not checked, we'll only allow the owner to add hosts"))
    # available means "nameserver for domain operating and reachable" -
    # gets set to False if we have trouble reaching the nameserver
    available = models.BooleanField(
        _("available"),
        default=False,
        help_text=_("Check if nameserver is available/reachable - "
                    "if not checked, we'll pause querying/updating this nameserver for a while"))
    comment = models.CharField(
        _("comment"),
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text=_("Some arbitrary comment about your domain. "
                    "If your domain is public, the comment will be also publicly shown."))

    last_update = models.DateTimeField(_("last update"), auto_now=True)
    created = models.DateTimeField(_("created at"), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='domains', verbose_name=_("created by"),
                                   on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def generate_ns_secret(self):
        algorithm = self.nameserver_update_algorithm
        bitlength = UPDATE_ALGORITHMS[algorithm].bitlength
        user_model = get_user_model()
        secret = user_model.objects.make_random_password(length=bitlength // 8)
        secret = secret.encode('utf-8')
        self.nameserver_update_secret = secret_base64 = base64.b64encode(secret)
        self.save()
        return secret_base64

    def get_bind9_algorithm(self):
        return UPDATE_ALGORITHMS.get(self.nameserver_update_algorithm).bind_name

    class Meta:
        verbose_name = _('domain')
        verbose_name_plural = _('domains')
        ordering = ('name',)


@python_2_unicode_compatible
class Host(models.Model):
    name = models.CharField(
        _("name"),
        max_length=255,  # RFC 2181 (and considering having multiple joined labels here later)
        validators=[
            RegexValidator(
                regex=r'^(([a-z0-9][a-z0-9\-]*[a-z0-9])|[a-z0-9])$',
                message='Invalid host name: only "a-z", "0-9" and "-" is allowed'
            ),
            host_blacklist_validator,
        ],
        help_text=_("The name of your host."))
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, verbose_name=_("domain"))
    update_secret = models.CharField(
        _("update secret"),
        max_length=64,  # secret gets hashed (on save) to salted sha1, 58 bytes str len
    )
    comment = models.CharField(
        _("comment"),
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text=_("Some arbitrary comment about your host, e.g  who / what / where this host is"))

    # available means that this host may be updated (or not, if False) -
    # gets set to False if abuse happens (client malfunctioning) or
    # if updating this host triggers other errors or if host is considered stale:
    available = models.BooleanField(
        _("available"),
        default=True,
        help_text=_("Check if host is available/in use - "
                    "if not checked, we won't accept updates for this host"))
    netmask_ipv4 = models.PositiveSmallIntegerField(
        _("netmask IPv4"),
        default=32,
        help_text=_("Netmask/Prefix length for IPv4."))
    netmask_ipv6 = models.PositiveSmallIntegerField(
        _("netmask IPv6"),
        default=64,
        help_text=_("Netmask/Prefix length for IPv6."))
    # abuse means that we (either the operator or some automatic mechanism)
    # think the host is used in some abusive or unfair way, e.g.:
    # sending nochg updates way too often or otherwise using a defect,
    # misconfigured or otherwise malfunctioning update client
    # acting against fair use / ToS.
    # the abuse flag can be switched off by the user, if the user thinks
    # he fixed the problem on his side (or that there was no problem).
    abuse = models.BooleanField(
        _("abuse"),
        default=False,
        help_text=_("Checked if we think you abuse the service - "
                    "you may uncheck this AFTER fixing all issues on your side"))

    # similar to above, but can not be toggled by the user:
    abuse_blocked = models.BooleanField(
        _("abuse blocked"),
        default=False,
        help_text=_("Checked to block a host for abuse."))

    # count client misbehaviours, like sending nochg updates or other
    # errors that should make the client stop trying to update:
    client_faults = models.PositiveIntegerField(_("client faults"), default=0)
    client_result_msg = models.CharField(
        _("client result msg"),
        max_length=RESULT_MSG_LEN,
        default='', blank=True, null=True,
        help_text=_("Latest result message relating to the client"))

    # count server faults that happened when updating this host
    server_faults = models.PositiveIntegerField(_("server faults"), default=0)
    server_result_msg = models.CharField(
        _("server result msg"),
        max_length=RESULT_MSG_LEN,
        default='', blank=True, null=True,
        help_text=_("Latest result message relating to the server"))

    # count api auth errors - maybe caused by host owner (misconfigured update client)
    api_auth_faults = models.PositiveIntegerField(_("api auth faults"), default=0)
    api_auth_result_msg = models.CharField(
        _("api auth result msg"),
        max_length=RESULT_MSG_LEN,
        default='', blank=True, null=True,
        help_text=_("Latest result message relating to api authentication"))

    # when we received the last update for v4/v6 addr
    last_update_ipv4 = models.DateTimeField(_("last update IPv4"), blank=True, null=True)
    last_update_ipv6 = models.DateTimeField(_("last update IPv6"), blank=True, null=True)
    # how we received the last update for v4/v6 addr
    tls_update_ipv4 = models.BooleanField(_("TLS update IPv4"), default=False)
    tls_update_ipv6 = models.BooleanField(_("TLS update IPv6"), default=False)

    # for "hosts --stale-check --notify-user" management command
    staleness = models.PositiveIntegerField(_("staleness"), default=0)
    staleness_notification_timestamp = models.DateTimeField(_("staleness notification time"), blank=True, null=True)

    last_update = models.DateTimeField(_("last update"), auto_now=True)
    created = models.DateTimeField(_("created at"), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='hosts', verbose_name=_("created by"),
                                   on_delete=models.CASCADE)

    def __str__(self):
        return u"%s.%s" % (self.name, self.domain.name)

    class Meta(object):
        unique_together = (('name', 'domain'),)
        index_together = (('name', 'domain'),)
        verbose_name = _('host')
        verbose_name_plural = _('hosts')
        ordering = ('domain', 'name')  # groupby domain and sort by name

    def get_fqdn(self):
        return dnstools.FQDN(self.name, self.domain.name)

    @classmethod
    def get_by_fqdn(cls, fqdn, **kwargs):
        # Assuming subdomain has no dots (.) the fqdn is split at the first dot
        splitted = fqdn.split('.', 1)
        if len(splitted) != 2:
            raise ValueError("get_by_fqdn(%s): FQDN has to contain (at least) one dot" % fqdn)
        try:
            host = Host.objects.get(name=splitted[0], domain__name=splitted[1], **kwargs)
        except Host.DoesNotExist:
            return None
        except Host.MultipleObjectsReturned:
            # should not happen, see Meta.unique_together
            raise ValueError("get_by_fqdn(%s) found more than 1 host" % fqdn)
        else:
            return host

    def get_ip(self, kind):
        record = 'A' if kind == 'ipv4' else 'AAAA'
        try:
            return dnstools.query_ns(self.get_fqdn(), record)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return None
        except (dns.resolver.NoNameservers, dns.resolver.Timeout, dnstools.NameServerNotAvailable,
                dns.message.UnknownTSIGKey):
            return _('error')

    def get_ipv4(self):
        return self.get_ip('ipv4')

    def get_ipv6(self):
        return self.get_ip('ipv6')

    def poke(self, kind, secure):
        if kind == 'ipv4':
            self.last_update_ipv4 = now()
            self.tls_update_ipv4 = secure
        else:
            self.last_update_ipv6 = now()
            self.tls_update_ipv6 = secure
        self.save()

    def register_client_result(self, msg, fault=False):
        if fault:
            self.client_faults += 1
        self.client_result_msg = result_fmt(msg)
        self.save()

    def register_server_result(self, msg, fault=False):
        if fault:
            self.server_faults += 1
        self.server_result_msg = result_fmt(msg)
        self.save()

    def register_api_auth_result(self, msg, fault=False):
        if fault:
            self.api_auth_faults += 1
        self.api_auth_result_msg = result_fmt(msg)
        self.save()

    def generate_secret(self, secret=None):
        # note: we use a quick hasher for the update_secret as expensive
        # more modern hashes might put too much load on the servers. also
        # many update clients might use http without tls, so it is not too
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
        dnstools.delete(obj.get_fqdn())
    except (dnstools.Timeout, dnstools.NameServerNotAvailable):
        # well, we tried to clean up, but we didn't reach the nameserver
        pass
    except (dnstools.DnsUpdateError,):
        # e.g. PeerBadSignature if host is protected by a key we do not have
        pass


pre_delete.connect(pre_delete_host, sender=Host)


def post_save_host(sender, **kwargs):
    obj = kwargs['instance']
    if obj.abuse or obj.abuse_blocked:
        try:
            dnstools.delete(obj.get_fqdn())
        except (dnstools.Timeout, dnstools.NameServerNotAvailable):
            # well, we tried to clean up, but we didn't reach the nameserver
            pass
        except (dnstools.DnsUpdateError,):
            # e.g. PeerBadSignature if host is protected by a key we do not have
            pass


post_save.connect(post_save_host, sender=Host)


@python_2_unicode_compatible
class RelatedHost(models.Model):
    # host addr = network_of_main_host + interface_id
    name = models.CharField(
        _("name"),
        max_length=255,  # RFC 2181 (and considering having multiple joined labels here later)
        validators=[
            RegexValidator(
                regex=r'^(([a-z0-9][a-z0-9\-]*[a-z0-9])|[a-z0-9])$',
                message='Invalid host name: only "a-z", "0-9" and "-" is allowed'
            ),
        ],
        help_text=_("The name of a host in same network as your main host."))
    comment = models.CharField(
        _("comment"),
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text=_("Some arbitrary comment about your host, e.g  who / what / where this host is"))
    interface_id_ipv4 = models.CharField(
        _("interface ID IPv4"),
        default='', blank=True, null=True,
        max_length=16,
        help_text=_("The IPv4 interface ID of this host. Use IPv4 notation. Empty = do not set record."))
    interface_id_ipv6 = models.CharField(
        _("interface ID IPv6"),
        default='', blank=True, null=True,
        max_length=40,
        help_text=_("The IPv6 interface ID of this host. Use IPv6 notation. Empty = do not set record."))
    available = models.BooleanField(
        _("available"),
        default=True,
        help_text=_("Check if host is available/in use - "
                    "if not checked, we won't accept updates for this host"))

    main_host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name='relatedhosts',
        verbose_name=_("main host"))

    def __str__(self):
        return u"%s.%s" % (self.name, text_type(self.main_host))

    class Meta(object):
        unique_together = (('name', 'main_host'),)
        verbose_name = _('related host')
        verbose_name_plural = _('related hosts')
        ordering = ('main_host', 'name')

    def get_fqdn(self):
        main = self.main_host.get_fqdn()
        # note: we put the related hosts (subhosts) into same zone as the main host,
        # so the resulting hostname has a dot inside:
        return dnstools.FQDN('%s.%s' % (self.name, main.host), main.domain)

    def get_ip(self, kind):
        record = 'A' if kind == 'ipv4' else 'AAAA'
        try:
            return dnstools.query_ns(self.get_fqdn(), record)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return 'none'
        except (dns.resolver.NoNameservers, dns.resolver.Timeout, dnstools.NameServerNotAvailable):
            return 'error'

    def get_ipv4(self):
        return self.get_ip('ipv4')

    def get_ipv6(self):
        return self.get_ip('ipv6')


pre_delete.connect(pre_delete_host, sender=RelatedHost)


@python_2_unicode_compatible
class ServiceUpdater(models.Model):
    name = models.CharField(
        _("name"),
        max_length=32,
        help_text=_("Service name"))
    comment = models.CharField(
        _("comment"),
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text=_("Some arbitrary comment about the service"))
    server = models.CharField(
        _("server"),
        max_length=255,  # should be enough
        help_text=_("Update Server [name or IP] of this service"))
    path = models.CharField(
        _("path"),
        max_length=255,  # should be enough
        default='/nic/update',
        help_text=_("Update Server URL path of this service"))
    secure = models.BooleanField(
        _("secure"),
        default=True,
        help_text=_("Use https / TLS to contact the Update Server?"))

    # what kind(s) of IPs is (are) acceptable to this service:
    accept_ipv4 = models.BooleanField(_("accept IPv4"), default=False)
    accept_ipv6 = models.BooleanField(_("accept IPv6"), default=False)

    last_update = models.DateTimeField(_("last update"), auto_now=True)
    created = models.DateTimeField(_("created at"), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='serviceupdater',
        verbose_name=_("created by"), on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta(object):
        verbose_name = _('service updater')
        verbose_name_plural = _('service updaters')


@python_2_unicode_compatible
class ServiceUpdaterHostConfig(models.Model):
    service = models.ForeignKey(ServiceUpdater, on_delete=models.CASCADE, verbose_name=_("service"))

    hostname = models.CharField(
        _("hostname"),
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text=_("The hostname for that service (used in query string)"))
    comment = models.CharField(
        _("comment"),
        max_length=255,  # should be enough
        default='', blank=True, null=True,
        help_text=_("Some arbitrary comment about your host on that service"))
    # credentials for http basic auth for THAT service (not for us),
    # we need to store the password in plain text, we can't hash it
    name = models.CharField(
        _("name"),
        max_length=255,  # should be enough
        help_text=_("The name/id for that service (used for http basic auth)"))
    password = models.CharField(
        _("password"),
        max_length=255,  # should be enough
        help_text=_("The password/secret for that service (used for http basic auth)"))

    # what kind(s) of IPs should be given to this service:
    give_ipv4 = models.BooleanField(_("give IPv4"), default=False)
    give_ipv6 = models.BooleanField(_("give IPv6"), default=False)

    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name='serviceupdaterhostconfigs',
        verbose_name=_("host"))

    last_update = models.DateTimeField(_("last update"), auto_now=True)
    created = models.DateTimeField(_("created at"), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='serviceupdaterhostconfigs',
        verbose_name=_("created by"), on_delete=models.CASCADE)

    def __str__(self):
        return u"%s (%s)" % (self.hostname, self.service.name,)

    class Meta(object):
        verbose_name = _('service updater host config')
        verbose_name_plural = _('service updater host configs')
