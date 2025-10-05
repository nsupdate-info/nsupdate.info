from django.urls import re_path
from django.views.generic.base import TemplateView

from registration.backends.default.views import ActivationView
from registration.backends.default.views import RegistrationView

from .views import UserProfileView, DeleteUserView, UserChangePasswordView


urlpatterns = (
    re_path(r'^profile/', UserProfileView.as_view(), name="account_profile"),
    re_path(r'^settings/', UserChangePasswordView.as_view(), name='account_settings'),
    re_path(r'^delete/', DeleteUserView.as_view(), name="account_delete"),

    # Registration start
    re_path(r'^activate/complete/$',
            TemplateView.as_view(template_name='registration/activation_complete.html'),
            name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.

    re_path(r'^activate/(?P<activation_key>\w+)/$',
            ActivationView.as_view(),
            name='registration_activate'),
    re_path(r'^register/$',
            RegistrationView.as_view(),
            name='registration_register'),
    re_path(r'^register/complete/$',
            TemplateView.as_view(template_name='registration/registration_complete.html'),
            name='registration_complete'),
    re_path(r'^register/closed/$',
            TemplateView.as_view(template_name='registration/registration_closed.html'),
            name='registration_disallowed'),
    # Registration end
)
