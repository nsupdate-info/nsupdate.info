"""
settings for production
"""

from .base import *

DEBUG = False

WE_HAVE_TLS = True  # True if you run a https site also, suggest that site to users if they work on the http site.
CSRF_COOKIE_SECURE = WE_HAVE_TLS
SESSION_COOKIE_SECURE = WE_HAVE_TLS

# these are the service host names we deal with
BASEDOMAIN = 'nsupdate.info'
# do NOT just use the BASEDOMAIN for WWW_HOST, or you will run into troubles
# when you want to be on publicsuffix.org list and still be able to set cookies
WWW_HOST = 'www.' + BASEDOMAIN  # a host with a ipv4 and a ipv6 address
# hosts to enforce a v4 / v6 connection (to determine the respective ip)
WWW_IPV4_HOST = 'ipv4.' + BASEDOMAIN  # a host with ONLY a ipv4 address
WWW_IPV6_HOST = 'ipv6.' + BASEDOMAIN  # a host with ONLY a ipv6 address

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [WWW_HOST, WWW_IPV4_HOST, WWW_IPV6_HOST]
