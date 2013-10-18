import pytest

from django.utils.translation import activate


# Note: fixture must be "function" scope (default), see https://github.com/pelme/pytest_django/issues/33
@pytest.fixture(autouse=True)
def db_init(db):
    """
    Init the database contents for testing, so we have a service domain, ...
    """
    from nsupdate.main.models import Domain
    from django.db import IntegrityError
    Domain.objects.create(domain='nsupdate.info',
                          nameserver_ip='85.10.192.104',
                          nameserver_update_algorithm='HMAC_SHA512',
                          nameserver_update_key='YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYQ==',
                          available_for_everyone=True)


def pytest_runtest_setup(item):
    activate('en')
