from django.conf.urls import patterns, url

from .views import UserProfileView


urlpatterns = patterns(
    '',
    url(r'^profile/', UserProfileView.as_view(), name="account_profile"),
)
