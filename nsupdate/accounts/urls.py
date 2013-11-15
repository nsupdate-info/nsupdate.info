from django.conf.urls import patterns, url
from django.contrib.auth.views import password_change

from .views import UserProfileView


urlpatterns = patterns(
    '',
    url(r'^profile/', UserProfileView.as_view(), name="account_profile"),
)
