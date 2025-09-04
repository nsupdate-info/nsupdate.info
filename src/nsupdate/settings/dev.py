"""
Settings for development and unit tests.
"""

from .base import *

DEBUG = True

SECRET_KEY = 'UNSECURE_BECAUSE_WE_ARE_DEVELOPING'
WE_HAVE_TLS = False  # True if you also run an HTTPS site; suggest that site to users if they are on the HTTP site.
CSRF_COOKIE_SECURE = WE_HAVE_TLS
SESSION_COOKIE_SECURE = WE_HAVE_TLS

BASEDOMAIN = 'nsupdate.info'
WWW_HOST = 'localhost:8000'
# For debugging IP detection on localhost:
WWW_IPV4_HOST = 'localhost:8000'
WWW_IPV6_HOST = 'ip6-localhost:8000'

# ALLOWED_HOSTS is not needed here, as DEBUG is True.

MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE
INTERNAL_IPS = ['127.0.0.1', '::1']  # Needed for the Debug Toolbar.

DEBUG_TOOLBAR_PATCH_SETTINGS = False
INSTALLED_APPS += (
    'debug_toolbar',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
