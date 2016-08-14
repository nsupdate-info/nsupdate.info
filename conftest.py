"""
configuration for the (py.test based) tests
"""

import pytest

from random import randint

from nsupdate.main.dnstools import FQDN

from django.conf import settings

# this is to create a Domain entries in the database, so they can be used for unit tests:
BASEDOMAIN = "nsupdate.info"
TESTDOMAIN = "tests." + BASEDOMAIN
TEST_HOST = FQDN('test%da' % randint(1, 1000000), TESTDOMAIN)  # unit tests can update this host ONLY
TEST_SECRET = "secret"
TEST_HOST2 = FQDN('test%db' % randint(1, 1000000), TESTDOMAIN)
TEST_SECRET2 = "somethingelse"
RELATED_HOST_NAME = 'rh'
TEST_HOST_RELATED = FQDN(RELATED_HOST_NAME + '.' + TEST_HOST.host, TEST_HOST.domain)
NAMESERVER_IP = "127.0.0.1"
NAMESERVER2_IP = NAMESERVER_IP  # use same server as tests query shortly after update, too quick for secondary
NAMESERVER_UPDATE_ALGORITHM = "HMAC_SHA512"
# no problem, you can ONLY update the TESTDOMAIN with this secret, nothing else:
NAMESERVER_UPDATE_SECRET = "YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYQ=="
NAMESERVER_PUBLIC = True

USERNAME = 'test'
USERNAME2 = 'test2'
PASSWORD = 'pass'

HOSTNAME = 'nsupdate-ddns-client-unittest.' + BASEDOMAIN
_PASSWORD = 'yUTvxjRwNu'  # no problem, is only used for this unit test
SERVER = 'ipv4.' + BASEDOMAIN
SECURE = False  # TLS/SNI support on python 2.x sucks :(

from django.utils.translation import activate

from nsupdate.main.dnstools import update_ns, FQDN


@pytest.yield_fixture(scope="function")
def ddns_hostname():
    """
    get a random hostname for tests and make sure it is removed from dns
    after the test
    """
    hostname = "test%d" % randint(1000000000, 2000000000)
    yield hostname
    fqdn = FQDN(hostname, TESTDOMAIN)
    update_ns(fqdn, 'A', action='del')
    update_ns(fqdn, 'AAAA', action='del')


@pytest.yield_fixture(scope="function")
def ddns_fqdn(ddns_hostname):
    yield FQDN(ddns_hostname, TESTDOMAIN)


# Note: fixture must be "function" scope (default), see https://github.com/pelme/pytest_django/issues/33
@pytest.fixture(autouse=True)
def db_init(db):  # note: db is a predefined fixture and required here to have the db available
    """
    Init the database contents for testing, so we have a service domain, ...
    """
    from django.contrib.auth import get_user_model
    from nsupdate.main.models import Host, RelatedHost, Domain, ServiceUpdater, ServiceUpdaterHostConfig
    user_model = get_user_model()
    # create a fresh test user
    u = user_model.objects.create_user(USERNAME, settings.DEFAULT_FROM_EMAIL, PASSWORD)
    u.save()
    u2 = user_model.objects.create_user(USERNAME2, 'test@example.org', PASSWORD)
    u2.save()
    # this is for tests:
    dt = Domain.objects.create(
        name=TESTDOMAIN,  # special: test-domain update secret!
        nameserver_ip=NAMESERVER_IP,
        nameserver2_ip=NAMESERVER2_IP,
        nameserver_update_algorithm=NAMESERVER_UPDATE_ALGORITHM,
        nameserver_update_secret=NAMESERVER_UPDATE_SECRET,
        public=NAMESERVER_PUBLIC,
        available=True,
        created_by=u,
    )
    # this is for querying:
    d = Domain.objects.create(
        name=BASEDOMAIN,
        nameserver_ip=NAMESERVER_IP,
        nameserver2_ip=NAMESERVER2_IP,
        nameserver_update_algorithm=NAMESERVER_UPDATE_ALGORITHM,
        nameserver_update_secret='invalid=',  # we don't send updates there (and the real key is really secret)
        public=NAMESERVER_PUBLIC,
        available=True,
        created_by=u2,
    )
    # a Host for api / session update tests
    hostname = TEST_HOST.host
    h = Host(name=hostname, domain=dt, created_by=u, netmask_ipv4=29, netmask_ipv6=64)
    h.generate_secret(secret=TEST_SECRET)
    hostname2 = TEST_HOST2.host
    h2 = Host(name=hostname2, domain=dt, created_by=u2, netmask_ipv4=29, netmask_ipv6=64)
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

    RelatedHost.objects.create(name=RELATED_HOST_NAME,
                               interface_id_ipv4="0.0.0.1", interface_id_ipv6="::1", main_host=h)
    RelatedHost.objects.create(name=RELATED_HOST_NAME,
                               interface_id_ipv4="0.0.0.1", interface_id_ipv6="::1", main_host=h2)


def pytest_runtest_setup(item):
    activate('en')
