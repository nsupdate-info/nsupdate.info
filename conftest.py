"""
configuration for the (py.test based) tests
"""

import pytest

from django.conf import settings

# this is to create a Domain entries in the database, so they can be used for unit tests:
BASEDOMAIN = "nsupdate.info"
TEST_HOST = 'test.' + BASEDOMAIN  # unit tests can update this host ONLY
TEST_SECRET = "secret"
TEST_HOST2 = 'test2.' + BASEDOMAIN
TEST_SECRET2 = "somethingelse"
NAMESERVER_IP = "85.10.192.104"
NAMESERVER_UPDATE_ALGORITHM = "HMAC_SHA512"
# no problem, you can ONLY update the TEST_HOST with this secret, nothing else:
NAMESERVER_UPDATE_SECRET = "YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYQ=="
NAMESERVER_PUBLIC = True

USERNAME = 'test'
USERNAME2 = 'test2'
PASSWORD = 'pass'

HOSTNAME = 'nsupdate-ddns-client-unittest.' + BASEDOMAIN
_PASSWORD = 'yUTvxjRwNu'  # no problem, is only used for this unit test
SERVER = 'ipv4.' + BASEDOMAIN
SECURE = False  # SSL/SNI support on python 2.x sucks :(

from django.utils.translation import activate


# Note: fixture must be "function" scope (default), see https://github.com/pelme/pytest_django/issues/33
@pytest.fixture(autouse=True)
def db_init(db):  # note: db is a predefined fixture and required here to have the db available
    """
    Init the database contents for testing, so we have a service domain, ...
    """
    from django.contrib.auth import get_user_model
    from nsupdate.main.models import Host, Domain, ServiceUpdater, ServiceUpdaterHostConfig
    user_model = get_user_model()
    # create a fresh test user
    u = user_model.objects.create_user(USERNAME, settings.DEFAULT_FROM_EMAIL, PASSWORD)
    u.save()
    u2 = user_model.objects.create_user(USERNAME2, 'test@example.org', PASSWORD)
    u2.save()
    # this is for updating:
    Domain.objects.create(
        domain=TEST_HOST,  # special: single-host update secret!
        nameserver_ip=NAMESERVER_IP,
        nameserver_update_algorithm=NAMESERVER_UPDATE_ALGORITHM,
        nameserver_update_secret=NAMESERVER_UPDATE_SECRET,
        public=NAMESERVER_PUBLIC,
        created_by=u,
    )
    # this is for querying:
    d = Domain.objects.create(
        domain=BASEDOMAIN,
        nameserver_ip=NAMESERVER_IP,
        nameserver_update_algorithm=NAMESERVER_UPDATE_ALGORITHM,
        nameserver_update_secret='invalid=',  # we don't send updates there (and the real key is really secret)
        public=NAMESERVER_PUBLIC,
        created_by=u2,
    )
    # a Host for api / session update tests
    h = Host(subdomain='test', domain=d, created_by=u)
    h.generate_secret(secret=TEST_SECRET)
    h2 = Host(subdomain='test2', domain=d, created_by=u2)
    h2.generate_secret(secret=TEST_SECRET2)

    # "update other service" ddns_client feature
    s = ServiceUpdater.objects.create(
        name='nsupdate',
        server=SERVER,
        secure=SECURE,
        accept_ipv4=True,
        accept_ipv6=False,
        created_by=u,
    )
    ServiceUpdaterHostConfig.objects.create(
        hostname=None,  # not needed for nsupdate.info, see below
        name=HOSTNAME,
        password=_PASSWORD,
        service=s,
        host=h,
        give_ipv4=True,
        give_ipv6=False,
        created_by=u,
    )


def pytest_runtest_setup(item):
    activate('en')
