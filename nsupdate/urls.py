from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^account/', include('nsupdate.accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('nsupdate.main.urls')),
)

from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
                            url(r'^static/(?P<path>.*)$', 'serve'), )
