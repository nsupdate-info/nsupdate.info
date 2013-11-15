from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import views as auth_views

admin.autodiscover()

from registration.backends.default.views import ActivationView
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationForm


class Html5RegistrationForm(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super(Html5RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(dict(autofocus=None))


class Html5AuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(Html5AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(dict(autofocus=None))


def html5_login(*args, **kwargs):
    kwargs['authentication_form'] = Html5AuthenticationForm
    return auth_views.login(*args, **kwargs)


class Html5PasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(Html5PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update(dict(autofocus=None))


def html5_password_change(*args, **kwargs):
    kwargs['password_change_form'] = Html5PasswordChangeForm
    kwargs['template_name'] = 'registration/password_change.html'  # own template
    kwargs['post_change_redirect'] = reverse('account_profile')
    return auth_views.password_change(*args, **kwargs)


urlpatterns = patterns(
    '',
    url('', include('social.apps.django_app.urls', namespace='social')),
    # registration start
    # this is a modified copy of registration.backends.default.urls:
    url(r'^accounts/activate/complete/$',
        TemplateView.as_view(template_name='registration/activation_complete.html'),
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^accounts/activate/(?P<activation_key>\w+)/$',
        ActivationView.as_view(),
        name='registration_activate'),
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=Html5RegistrationForm),
        name='registration_register'),
    url(r'^accounts/register/complete/$',
        TemplateView.as_view(template_name='registration/registration_complete.html'),
        name='registration_complete'),
    url(r'^accounts/register/closed/$',
        TemplateView.as_view(template_name='registration/registration_closed.html'),
        name='registration_disallowed'),
    # from registration.auth_urls:
    url(r'^accounts/login/$',
        html5_login,
        {'template_name': 'registration/login.html'},
        name='auth_login'),
    url(r'^accounts/logout/$',
        auth_views.logout,
        {'template_name': 'registration/logout.html'},
        name='auth_logout'),
    url(r'^accounts/password/change/$',
        html5_password_change,
        name='auth_password_change'),
    url(r'^accounts/password/change/done/$',
        auth_views.password_change_done,
        name='auth_password_change_done'),
    url(r'^accounts/password/reset/$',
        auth_views.password_reset,
        name='auth_password_reset'),
    url(r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='auth_password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),
    url(r'^accounts/password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'),
    # registration end
    url(r'^account/', include('nsupdate.accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('nsupdate.main.urls')),
)

from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
                            url(r'^static/(?P<path>.*)$', 'serve'), )
