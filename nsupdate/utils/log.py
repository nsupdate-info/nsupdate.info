"""
logger decorator to enable logging of infos from django's HttpRequest object.

Usage:

    Code:

    @log.logger(__name__)
    def home(request, logger=None):
        logger.info('user performed some action')

    Class based views work the same way, just decorate/modify the view's METHOD(s).

    Logging formatter configuration:

    'format': '[%(asctime)s] %(levelname)s %(message)s ' \
              '[ip: %(request.meta.remote_addr)s, ua: "%(request.meta.http_user_agent)s"]'

Based on code from:
    https://derrickpetzold.com/p/django-requst-logging-json/
    which is (c) Derrick Petzold - with a Creative Commons BY-SA license.
"""

import socket
import logging

from django.http.request import HttpRequest


class RequestInfo(object):

    def __init__(self, request):
        self.request = request

    def __getitem__(self, name):
        if name == 'request.host':
            return socket.gethostname()

        if name.startswith('request.meta.'):
            val = name.split('.')[2]
            try:
                return self.request.META[val.upper()]
            except KeyError as e:
                return None
        return eval('self.%s' % (name))

    def _get_attrs(self, obj, excluded=None):
        if excluded is None:
            excluded = set()
        attrs = []
        for attr in dir(obj):
            if attr not in excluded:
                try:
                    if not attr.startswith('_') and \
                            not callable(getattr(obj, attr)):
                        attrs.append(attr)
                except AttributeError:
                    pass
        return attrs

    def __iter__(self):
        keys = ['request.host']
        keys.extend(['request.%s' % (a, )
                     for a in self._get_attrs(self.request, set(['raw_post_data', ]))])
        keys.extend(['request.session.%s' % (a, )
                     for a in self._get_attrs(self.request.session)])
        keys.extend(['request.user.%s' % (a, )
                     for a in self._get_attrs(self.request.user)])
        keys.extend(['request.meta.%s' % (a.lower(), )
                     for a in self.request.META.keys()])
        return keys.__iter__()


def logger(name):
    def wrap(func):
        def caller(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, HttpRequest):
                    request = arg
            if 'logger' not in kwargs:
                if request is not None:
                    kwargs['logger'] = logging.LoggerAdapter(
                        logging.getLogger(name), RequestInfo(request))
                else:
                    kwargs['logger'] = logging.getLogger(name)
            return func(*args, **kwargs)
        return caller
    return wrap
