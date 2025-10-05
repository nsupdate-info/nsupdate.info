"""
Settings for production.
"""

from .base import *

DEBUG = False

WE_HAVE_TLS = True  # True if you also run an HTTPS site; suggest that site to users if they are on the HTTP site.
CSRF_COOKIE_SECURE = WE_HAVE_TLS
SESSION_COOKIE_SECURE = WE_HAVE_TLS

# These are the service hostnames we deal with.
BASEDOMAIN = 'nsupdate.info'
# Do NOT just use the BASEDOMAIN for WWW_HOST, or you will run into trouble
# when you want to be on the publicsuffix.org list and still be able to set cookies.
WWW_HOST = 'www.' + BASEDOMAIN  # A host with an IPv4 and an IPv6 address.
# Hosts to enforce a v4/v6 connection (to determine the respective IP).
WWW_IPV4_HOST = 'ipv4.' + BASEDOMAIN  # A host with ONLY an IPv4 address.
WWW_IPV6_HOST = 'ipv6.' + BASEDOMAIN  # A host with ONLY an IPv6 address.

# Hosts/domain names that are valid for this site; required if DEBUG is False.
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [WWW_HOST, WWW_IPV4_HOST, WWW_IPV6_HOST]
