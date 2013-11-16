from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import views as auth_views

admin.autodiscover()

from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationForm


def remember_me_login(request, *args, **kw):
    """
    Wraps the default login view function. If user does not want to be
    remembered, we change the cookie to a session cookie that gets cleared
    when the browser is closed.
    """
    if request.method == 'POST':
        if not request.POST.get('remember_me'):
            request.session.set_expiry(0)
    return auth_views.login(request, *args, **kw)


class Html5RegistrationForm(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super(Html5RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(dict(autofocus=None))


class Html5AuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(Html5AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(dict(autofocus=None))


class Html5PasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(Html5PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update(dict(autofocus=None))


urlpatterns = patterns(
    '',
    url('', include('social.apps.django_app.urls', namespace='social')),
    # registration start
    # these are some modified patterns from registration.backends.default.urls:
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=Html5RegistrationForm),
        name='registration_register'),
    # from registration.auth_urls:
    url(r'^accounts/login/$',
        remember_me_login,
        {'authentication_form': Html5AuthenticationForm,
         'template_name': 'registration/login.html'},
        name='auth_login'),
    url(r'^accounts/password/change/$',
        auth_views.password_change,
        {'password_change_form': Html5PasswordChangeForm,
         'template_name': 'registration/password_change.html',  # own template
         'post_change_redirect': '/account/profile'},  # reverse() does not work here
        name='auth_password_change'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    # registration end
    url(r'^account/', include('nsupdate.accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('nsupdate.main.urls')),
)

from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
                            url(r'^static/(?P<path>.*)$', 'serve'), )
