"""
top-level url dispatching
"""

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views


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


urlpatterns = patterns(
    '',
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^accounts/', include('nsupdate.login.urls')),
    # registration and user settings
    url(r'^account/', include('nsupdate.accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^', include('nsupdate.main.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
                            url(r'^static/(?P<path>.*)$', 'serve'), )
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
    )
