import pytest

from django.contrib.auth.hashers import check_password

from nsupdate.main.models import Host
from nsupdate.api.views import check_api_auth
from nsupdate.conftest import TEST_HOST


@pytest.mark.django_db
def test_sha1_to_weakargon2_upgrade():
    # TEST_HOST and TEST_SECRET are already in the db from conftest.py's db_init fixture
    # TEST_HOST is a FQDN object, we must convert it to string for get_by_fqdn
    host = Host.get_by_fqdn(str(TEST_HOST))
    assert host is not None

    # 1. Manually set a legacy SHA1 hash
    password = "RKjaZ9ZB4h"  # one-time password
    encoded = "sha1$Rg8V2HhaEqy9sBaKSyzQ3b$1a1a9d81afa2eadf205abb19a54b5e0cab60d09d"

    host.update_secret = encoded
    host.save()

    # Verify check_password works with our custom SHA1PasswordHasher
    assert check_password(password, host.update_secret)

    # 2. Test transparent upgrade in check_api_auth
    # check_api_auth should return the host and upgrade the secret to weakargon2
    authenticated_host = check_api_auth(str(host.get_fqdn()), password)

    assert authenticated_host is not None
    assert authenticated_host.pk == host.pk
    # It should have been upgraded to weakargon2
    assert authenticated_host.update_secret.startswith("weakargon2$")
    assert check_password(password, authenticated_host.update_secret)


@pytest.mark.django_db
def test_generate_secret_uses_weakargon2():
    host = Host.get_by_fqdn(str(TEST_HOST))
    host.generate_secret()
    assert host.update_secret.startswith("weakargon2$")


def test_weak_argon2_hasher():
    from django.contrib.auth.hashers import make_password, check_password
    password = "testpassword123"
    encoded = make_password(password, hasher='weakargon2')
    # Format: weakargon2$argon2id$v=19$m=8,t=1,p=1$...
    assert encoded.startswith("weakargon2$argon2id$")
    assert "m=8,t=1,p=1" in encoded
    assert check_password(password, encoded)
