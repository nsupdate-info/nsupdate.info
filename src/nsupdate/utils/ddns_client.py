"""
DynDNS2 client utilities.
"""

import logging
logger = logging.getLogger(__name__)

import requests
from requests import Timeout, ConnectionError  # Keep; re-exported from here.


TIMEOUT = 30.0  # Timeout for HTTP request response [s].


def dyndns2_update(name, password,
                   server, hostname=None, myip=None,
                   path='/nic/update', secure=True, timeout=TIMEOUT):
    """
    Send a DynDNS2-compatible update request.

    :param name: Username for HTTP basic auth
    :param password: Password for HTTP basic auth
    :param server: Server to send the update to
    :param hostname: Hostname to update
    :param myip: The new IP address for the hostname
    :param path: URL path (default: '/nic/update')
    :param secure: Whether to use TLS for the request (default: True)
                   Note: If you use secure=False, the given data will be
                   transmitted unencrypted.
    :param timeout: How long to wait until the response begins
    :return: Tuple (status_code, response_text)
    """
    params = {}
    if hostname is not None:
        params['hostname'] = hostname
    if myip is not None:
        params['myip'] = myip
    url = "%s://%s%s" % ('https' if secure else 'http', server, path)
    logger.debug("update request: %s %r" % (url, params, ))
    r = requests.get(url, params=params, auth=(name, password), timeout=timeout)
    r.close()
    logger.debug("update response: %d %s" % (r.status_code, r.text, ))
    return r.status_code, r.text.strip()
