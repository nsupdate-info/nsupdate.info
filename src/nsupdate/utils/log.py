"""
Logger decorator to enable logging of information from Django's HttpRequest object.

Usage:

    Code:

    @log.logger(__name__)
    def home(request, logger=None):
        logger.info('User performed some action')

    Class-based views work the same way; just decorate or modify the view's method(s).

    Logging formatter configuration:

    'format': '[%(asctime)s] %(levelname)s %(message)s ' \
              '[ip: %(request.META.REMOTE_ADDR)s, ua: "%(request.META.HTTP_USER_AGENT)s"]'

Based on code from (but heavily modified/refactored):
    https://derrickpetzold.com/p/django-requst-logging-json/
    which is (c) Derrick Petzold — Creative Commons BY-SA license.
"""

import logging

from django.http.request import HttpRequest


def _get_attrdict(obj, basename, excluded=None):
    """
    Get a dictionary of (basename-prefixed) attribute names/values,
    excluding the excluded names, internal attributes, and callables.

    :param obj: The object to inspect
    :param basename: The prefix for the names in the result dictionary
    :param excluded: Excluded attribute names; do not even touch (set or list)
    :return: Dict of names to values
    """
    if excluded is None:
        excluded = set()
    d = {}
    names = set(dir(obj)) - set(excluded)
    for name in names:
        if not name.startswith('_'):
            try:
                attr = getattr(obj, name)
                if not callable(attr):
                    d[basename + name] = attr
            except AttributeError:
                pass
    return d


def _get_elementdict(dct, basename, excluded=None):
    """
    Get a dictionary of (basename-prefixed) dictionary elements,
    excluding the excluded names.

    :param dct: The dict to inspect
    :param basename: The prefix for the names in the result dictionary
    :param excluded: Excluded dictionary keys (set or list)
    :return: Dict of names to values
    """
    if excluded is None:
        excluded = set()
    names = set(dct) - set(excluded)
    return dict((basename + name, dct[name]) for name in names)


def _build_request_info(request):
    """
    Build a dictionary with extra information extracted from the request object.

    :param request: Django HttpRequest object or None
    :return: Dict of names to values
    """
    d = {}
    if request:
        d.update(_get_elementdict(request.META, "request.META."))
        d.update(_get_attrdict(request, "request.", ['raw_post_data', ]))
        d.update(_get_attrdict(request.session, "request.session."))
        d.update(_get_attrdict(request.user, "request.user."))
    # Note: Avoid KeyErrors at least for the default logging format string.
    # Using a defaultdict as d does not help, as it gets iterated and keys/values
    # are transferred into a normal dict and then the logging format() is still
    # failing when it encounters an unknown key.
    # XXX This is ugly and prone to fail for other format strings.
    for key in ['request.META.REMOTE_ADDR',
                'request.META.HTTP_USER_AGENT',
                ]:
        if key not in d:
            d[key] = 'unknown'
    return d


def get_logger(name, request=None):
    """
    Get a logger providing extra information from the request.
    Use this if the decorator is not practical.

    :param name: Name of the logger
    :param request: Django's HttpRequest object
    :return: Logger instance
    """
    return logging.LoggerAdapter(logging.getLogger(name), _build_request_info(request))


def logger(name):
    """
    Decorator to provide extra information from the request to logging.

    :param name: Name of the logger
    :return: Decorated function or method
    """
    def wrap(func):
        def caller(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, HttpRequest):
                    request = arg
                    break
            if 'logger' not in kwargs:
                kwargs['logger'] = get_logger(name, request)
            return func(*args, **kwargs)
        return caller
    return wrap
