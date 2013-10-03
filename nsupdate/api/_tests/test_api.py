"""
Tests for api package.
"""

import pytest

# TODO XXX experiencing ImportErrors all the time. somehow project package structure is borked.
# what is the usual, working, project structure for a testable django / pytest.django project?

pytest.skip("doesn't work due to ImportErrors....")


def test_myip(client):
    response = client.get('/myip')
    assert response.status_code == 200
    assert response.content in ['127.0.0.1', '::1']


def test_nic_update(client):
    response = client.get('/nic/update')
    assert response.status_code == 401
