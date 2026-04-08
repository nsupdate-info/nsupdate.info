import pytest
from django.urls import reverse
from django.core.cache import cache
from nsupdate.api.utils import generate_detectip_token


@pytest.mark.django_db
def test_detect_ip_with_token(client):
    # 1. Create a session by doing something that saves it
    # We can just access client.session and it should be created if we save it
    s = client.session
    s['test_key'] = 'test_value'
    s.save()
    session_key = s.session_key
    assert session_key is not None

    # 2. Generate a token for this session
    token = generate_detectip_token(session_key)
    assert cache.get('detectip_token:%s' % token) == session_key

    # 3. Call DetectIpView with the token
    # We use a specific IP address to verify it's correctly detected
    test_ip = '1.2.3.4'
    url = reverse('detectip', args=(token,))
    response = client.get(url, REMOTE_ADDR=test_ip)

    # 4. Verify response
    assert response.status_code == 204

    # 5. Verify the session was updated with the new IP
    # We need to reload the session from the database/store
    # client.session will do that automatically on the next access
    updated_session = client.session
    assert updated_session.get('ipv4') == test_ip


@pytest.mark.django_db
def test_detect_ip_invalid_token(client):
    url = reverse('detectip', args=('invalidtoken',))
    response = client.get(url)
    assert response.status_code == 204
    # No crash, just returns 204
