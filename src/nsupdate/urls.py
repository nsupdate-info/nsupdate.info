"""
Top-level URL dispatcher.
"""

from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin
from django.contrib.auth import login
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView


def remember_me_login(request, *args, **kw):
    """
    Wrap the default login view function. If the user does not want to be
    remembered, change the cookie to a session cookie, which is cleared
    when the browser is closed.
    """
    if request.method == 'POST':
        if request.POST.get('remember_me'):
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
    return login(request, *args, **kw)


urlpatterns = [
    re_path('', include('social_django.urls', namespace='social')),
    re_path(r'^accounts/', include('nsupdate.login.urls')),
    # registration and user settings
    re_path(r'^account/', include('nsupdate.accounts.urls')),
    # https://wicg.github.io/change-password-url/index.html
    re_path(r'^.well-known/change-password$', RedirectView.as_view(pattern_name='account_settings', permanent=False)),
    re_path(r'^admin/', include((admin.site.get_urls(), 'admin'), namespace='admin')),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^', include('nsupdate.main.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns += [re_path(r'^__debug__/', include(debug_toolbar.urls)), ]


# We have expensive context processors and do not want to invoke them for the
# HTTP error views, so we must not use templates (or the Django default views).

def http_error(request, status, exception=None):
    if exception is not None:
        exception_repr = exception.__class__.__name__
        # Try to get an "interesting" exception message:
        try:
            message = exception.args[0]
        except (AttributeError, IndexError):
            pass
        else:
            if isinstance(message, str):
                exception_repr = message
    else:
        # We do not have an exception for HTTP 500.
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
