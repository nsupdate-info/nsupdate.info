# -*- coding: utf-8 -*-

import re

import logging
logger = logging.getLogger(__name__)

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationForm

import dns.resolver
import dns.name


resolver = dns.resolver.Resolver()
resolver.search = [dns.name.root, ]
resolver.lifetime = 5.0
resolver.nameservers = settings.NAMESERVERS


maildomain_blacklist = settings.MAILDOMAIN_BLACKLIST.strip().splitlines()


def check_mx(domain):
    valid = False
    try:
        mx_answers = resolver.query(domain, 'MX')
        # domain exists in DNS, domain has MX
        mx_entries = sorted([(mx_rdata.preference, mx_rdata.exchange) for mx_rdata in mx_answers])
        for preference, mx in mx_entries:
            try:
                addr_answers = resolver.query(mx, 'A')
            except dns.resolver.NoAnswer:
                addr_answers = resolver.query(mx, 'AAAA')
            # MX has IP addr
            mx_addrs = [addr_rdata.address for addr_rdata in addr_answers]
            for mx_addr in mx_addrs:
                if mx_addr not in (u'127.0.0.1', u'::1', u'0.0.0.0', ):
                    valid = True
                    break
            if valid:
                break
    except (dns.resolver.Timeout, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.NXDOMAIN, ):
        # expected exceptions (e.g. due to non-existing or misconfigured crap domains)
        pass
    return valid


def check_blacklist(domain):
    for blacklisted_re in maildomain_blacklist:
        if re.search(blacklisted_re, domain):
            return False
    return True


class RegistrationFormValidateEmail(RegistrationForm):
    def clean_email(self):
        """
        Validate the supplied email address to avoid undeliverable email and mailer daemon spam.
        """
        email = self.cleaned_data.get('email')
        valid_mx = False
        try:
            domain = email.split('@')[1]
            valid_mx = check_mx(domain)
        except Exception as e:
            logger.exception('RegistrationFormValidateEmail raised an exception:')
        not_blacklisted = check_blacklist(domain)
        if valid_mx and not_blacklisted:
            return email
        logger.info('RegistrationFormValidateEmail: rejecting email address %r' % email)
        raise forms.ValidationError(_("Enter a valid email address."))
