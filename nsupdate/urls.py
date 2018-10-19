"""
top-level url dispatching
"""

import six

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.http import HttpResponse


def remember_me_login(request, *args, **kw):
    """
    Wraps the default login view function. If user does not want to be
    remembered, we change the cookie to a session cookie that gets cleared
    when the browser is closed.
    """
    if request.method == 'POST':
        if request.POST.get('remember_me'):
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
    return auth_views.login(request, *args, **kw)


urlpatterns = [
    url('', include('social_django.urls', namespace='social')),
    url(r'^accounts/', include('nsupdate.login.urls')),
    # registration and user settings
    url(r'^account/', include('nsupdate.accounts.urls')),
    url(r'^admin/', include((admin.site.get_urls(), 'admin'), namespace='admin')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^', include('nsupdate.main.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]


# we have expensive context processors and do not want to invoke them for the
# http error views, so we must not use templates (nor the django default views).

def http_error(request, status, exception=None):
    if exception is not None:
        exception_repr = exception.__class__.__name__
        # Try to get an "interesting" exception message:
        try:
            message = exception.args[0]
        except (AttributeError, IndexError):
            pass
        else:
            if isinstance(message, six.text_type):
                exception_repr = message
    else:
        # we do not have an exception for 500
        exception_repr = 'Server Error'
    body = """\
<h1>%(exception)s (error %(status)d)</h1>
""" % dict(
        exception=exception_repr,
        status=status,
    )
    return HttpResponse(body, content_type='text/html', status=status)


def bad_request(request, exception, template_name=None):
    return http_error(request, 400, exception)


def permission_denied(request, exception, template_name=None):
    return http_error(request, 403, exception)


def page_not_found(request, exception, template_name=None):
    return http_error(request, 404, exception)


def server_error(request, template_name=None):
    return http_error(request, 500)


handler400 = 'nsupdate.urls.bad_request'
handler403 = 'nsupdate.urls.permission_denied'
handler404 = 'nsupdate.urls.page_not_found'
handler500 = 'nsupdate.urls.server_error'
