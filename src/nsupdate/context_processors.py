# -*- coding: utf-8 -*-
"""
Context processors for injecting some settings into the template context and
for keeping the IP addresses in the session fresh.
"""

import logging
logger = logging.getLogger(__name__)

import time

from .main.dnstools import put_ip_into_session
from .main.iptools import normalize_ip

from django.conf import settings
from django.db import OperationalError

MAX_IP_AGE = 180  # seconds


def add_settings(request):
    context = {}
    context['WWW_HOST'] = settings.WWW_HOST
    context['WWW_IPV4_HOST'] = settings.WWW_IPV4_HOST
    context['WWW_IPV6_HOST'] = settings.WWW_IPV6_HOST
    context['SERVICE_CONTACT'] = settings.SERVICE_CONTACT  # About view
    context['WE_HAVE_TLS'] = settings.WE_HAVE_TLS
    context['COOKIE_SECURE'] = settings.SESSION_COOKIE_SECURE or settings.CSRF_COOKIE_SECURE
    return context


def update_ips(request):
    """
    Update the IPs in the session using REMOTE_ADDR.
    Check the session for stale IPs and remove them if necessary.
    """
    # XXX Is a context processor the right place for this?
    s = request.session
    t_now = int(time.time())
    # Update and keep fresh using info from the request we have anyway:
    ipaddr = normalize_ip(request.META['REMOTE_ADDR'])
    put_ip_into_session(s, ipaddr, max_age=MAX_IP_AGE / 2)
    # Remove stale data to not show outdated IPs (e.g., after losing IPv6 connectivity):
    for key in ['ipv4', 'ipv6']:
        timestamp_key = "%s_timestamp" % key
        try:
            timestamp = s[timestamp_key]
        except KeyError:
            # Should always be there; initialize it:
            put_ip_into_session(s, '', kind=key)
        else:
            try:
                stale = timestamp + MAX_IP_AGE < t_now
            except (ValueError, TypeError):
                # Invalid timestamp in session.
                put_ip_into_session(s, '', kind=key)
            else:
                if stale:
                    logger.debug("ts: %s now: %s - killing stale %s (was: %s)" % (timestamp, t_now, key, s[key]))
                    # Clear the IP; it is not up-to-date anymore.
                    # Note: It is used to fill form fields, so set it to the empty string.
                    put_ip_into_session(s, '', kind=key)
    if s.session_key is None:
        # If we have a new session (== not loaded from database/storage), we
        # MUST save it here to create its session_key, as the base.html template
        # uses .session_key to build the URL for detectip:
        try:
            s.save()
        except OperationalError:
            # If, e.g., the database is locked (SQLite), do not raise here,
            # because it causes ugly tracebacks in emails even if Django
            # was just rendering the 404 template for the current request; see #356.
            pass
    return {}
