"""
top-level url dispatching
"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static


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
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^', include('nsupdate.main.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]
