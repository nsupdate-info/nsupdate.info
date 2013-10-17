"""
Tests for api package.
"""

import pytest


def test_myip(client):
    response = client.get('/myip')
    assert response.status_code == 200
    assert response.content in ['127.0.0.1', '::1']


def test_nic_update(client):
    response = client.get('/nic/update')
    assert response.status_code == 401
