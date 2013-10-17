from django.conf.urls import patterns, url
from django.contrib.auth.views import password_change

from .views import UserProfileView


urlpatterns = patterns(
    '',
    url(r'^profile/', UserProfileView.as_view(), name="account_profile"),
    url(r'^change_pw/', password_change, {
        'template_name': 'registration/password_change.html',
        'post_change_redirect': '/account/profile/', },
        name="password_change"), )
