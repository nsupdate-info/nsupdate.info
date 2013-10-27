"""
configuration for the tests
"""

import pytest

# put test_settings.py into the toplevel dir and invoke py.test from there
# needs to look like (just with YOUR domain, IP, algo, key, hostnames, IPs):
"""
# this is to create a Domain entry in the database, so it can be used for unit tests:
BASEDOMAIN = "nsupdate.info"
NAMESERVER_IP = "85.10.192.104"
NAMESERVER_UPDATE_ALGORITHM = "HMAC_SHA512"
NAMESERVER_UPDATE_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=="
NAMESERVER_PUBLIC = True

# for some unittests
WWW_HOST = BASEDOMAIN
NONEXISTING_HOST = 'nonexisting.' + BASEDOMAIN
WWW_IPV4_HOST = 'ipv4.' + BASEDOMAIN
WWW_IPV6_HOST = 'ipv6.' + BASEDOMAIN
WWW_IPV4_IP = '85.10.192.104'
WWW_IPV6_IP = '2a01:4f8:a0:2ffe:0:ff:fe00:8000'
"""

import test_settings

from django.utils.translation import activate


# Note: fixture must be "function" scope (default), see https://github.com/pelme/pytest_django/issues/33
@pytest.fixture(autouse=True)
def db_init(db):  # note: db is a predefined fixture and required here to have the db available
    """
    Init the database contents for testing, so we have a service domain, ...
    """
    from nsupdate.main.models import Domain
    Domain.objects.create(
        domain=test_settings.BASEDOMAIN,
        nameserver_ip=test_settings.NAMESERVER_IP,
        nameserver_update_algorithm=test_settings.NAMESERVER_UPDATE_ALGORITHM,
        nameserver_update_key=test_settings.NAMESERVER_UPDATE_KEY,
        public=test_settings.NAMESERVER_PUBLIC,
    )


def pytest_runtest_setup(item):
    activate('en')
