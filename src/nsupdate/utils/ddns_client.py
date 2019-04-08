"""
dyndns2 client
"""

import logging
logger = logging.getLogger(__name__)

import requests
from requests import Timeout, ConnectionError  # keep, is imported from here


TIMEOUT = 30.0  # timeout for http request response [s]


def dyndns2_update(name, password,
                   server, hostname=None, myip=None,
                   path='/nic/update', secure=True, timeout=TIMEOUT):
    """
    send a dyndns2-compatible update request

    :param name: for http basic auth
    :param password: for http basic auth
    :param server: server to send the update to
    :param hostname: hostname we want to update
    :param myip: the new ip address for hostname
    :param path: url path (default: '/nic/update')
    :param secure: whether to use tls for the request (default: True)
                   note: if you use secure=False, it will transmit
                   the given data unencrypted.
    :param timeout: how long to wait until response has to begin
    :return:
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
